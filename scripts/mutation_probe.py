#!/usr/bin/env python
"""S6-B3296 (L959 mechanism, B3139q-r110): the mutation probe as a repo tool.

#226 asks every pin to be proven able to fail; the harness that did it lived
in the scratchpad and was rewritten per batch (r105, r107, r108), and at r107
it rewrote three scripts on disk while a live sweep that reads them was running
(L959, a #292 instance - a measurement of one tree while its code moves).
This tool carries the two rules the scratchpad copies did not:

  1. REFUSE while any live python process names a target file on its command
     line (the reader of that file is running); --allow-live records the
     override into the result so the close can disclose it.
  2. Back up every target before the first write; restore each target by
     bytes after its case and assert the sha; and refuse an anchor that does
     not occur exactly once (#323).
  3. Run each pin ONCE on the UNMUTATED tree first and refuse a case whose
     pin is already red - a red pin 'kills' every mutant (L686; MEASURED at
     B3139q-r110: 5 of 5 reported killed against a failing test_b3293).

A case file (JSON) lists {file, test, label, anchor, mutant}; the tool runs
each pin with the mutant in place and reports killed / survived, exits 0 only
when every mutant was killed and every restore was byte-identical. Pinned by
test_b3296 (the live-reader refusal on an injected process list, the anchor
refusal, the restore).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "EXECUTION_QUEUE.md").is_file():          # L846 marker rule
    raise SystemExit("REFUSED: repo root not found from this file's location")


def live_readers(targets: list, processes=None) -> dict:
    """{target: [command lines]} for every live python process whose command
    line names the target (by basename). `processes` is the injection seam
    (#241); production asks Windows for the live list."""
    if processes is None:
        processes = _windows_python_processes()
    out: dict = {}
    for t in targets:
        base = Path(t).name
        hits = [c for c in processes if base in c]
        if hits:
            out[str(t)] = hits
    return out


def _windows_python_processes() -> list:
    cmd = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
           "Select-Object -ExpandProperty CommandLine")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        # L642: an unreadable process list is not an empty one - fail closed
        raise SystemExit(f"REFUSED (S6-B3296): could not read the live process list ({exc!r}); "
                         "nothing was written. Pass --processes-from <file> to supply one.")
    if r.returncode != 0:
        raise SystemExit(f"REFUSED (S6-B3296): the process-list query failed (exit {r.returncode}): "
                         f"{(r.stderr or '').strip()[:200]}")
    me = str(Path(__file__).name)
    return [ln for ln in (r.stdout or "").splitlines()
            if ln.strip() and me not in ln and "pytest" not in ln]


def run_cases(cases: list, *, allow_live: bool = False, processes=None,
              runner=None) -> dict:
    """Run every case; returns the report. `runner(test_id) -> returncode` is
    the injection seam for the pytest call."""
    targets = sorted({c["file"] for c in cases})
    live = live_readers(targets, processes)
    if live and not allow_live:
        raise SystemExit("REFUSED (S6-B3296 / L959): a live process reads a target - "
                         + "; ".join(f"{k}: {len(v)} process(es)" for k, v in live.items())
                         + ". Wait for it to exit, or pass --allow-live (recorded).")
    backups = {}
    for t in targets:
        p = ROOT / t
        backups[t] = p.read_bytes()
    results = []
    control: dict = {}
    try:
        for c in cases:
            # L686: the pin must be GREEN on the unmutated tree, or a mutant
            # cannot be told from the defect - one control run per test id
            if c["test"] not in control:
                control[c["test"]] = (runner or _pytest)(c["test"])
            if control[c["test"]] != 0:
                results.append({"label": c["label"], "status": "REFUSED",
                                "reason": f"pin is RED on the unmutated tree (exit "
                                          f"{control[c['test']]}) - nothing to prove (L686)"})
                continue
            p = ROOT / c["file"]
            orig = backups[c["file"]]
            txt = orig.decode("utf-8")
            nl = "\r\n" if txt.count("\r\n") * 2 > txt.count("\n") else "\n"
            anchor, mutant = c["anchor"].replace("\n", nl), c["mutant"].replace("\n", nl)
            n = txt.count(anchor)
            if n != 1:
                results.append({"label": c["label"], "status": "REFUSED",
                                "reason": f"anchor occurs {n} times, not once (#323)"})
                continue
            p.write_bytes(txt.replace(anchor, mutant).encode("utf-8"))
            try:
                rc = (runner or _pytest)(c["test"])
            finally:
                p.write_bytes(orig)
            restored = hashlib.sha256(p.read_bytes()).hexdigest() == hashlib.sha256(orig).hexdigest()
            results.append({"label": c["label"], "status": "killed" if rc != 0 else "SURVIVED",
                            "pytest_exit": rc, "restored_byte_identical": restored})
    finally:
        for t, b in backups.items():
            (ROOT / t).write_bytes(b)
    killed = sum(r["status"] == "killed" for r in results)
    return {"cases": len(cases), "killed": killed,
            "survived": [r["label"] for r in results if r["status"] == "SURVIVED"],
            "refused": [r["label"] for r in results if r["status"] == "REFUSED"],
            "restored_all": all(r.get("restored_byte_identical", True) for r in results),
            "live_readers_overridden": live if allow_live else {},
            "results": results}


def _pytest(test_id: str) -> int:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", test_id],
                       cwd=ROOT, capture_output=True, text=True, timeout=1800)
    return r.returncode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cases", required=True, help="JSON list of {file, test, label, anchor, mutant}")
    ap.add_argument("--out", default=None, help="write the report here (JSON)")
    ap.add_argument("--allow-live", action="store_true",
                    help="run even though a live process reads a target (recorded in the report)")
    ap.add_argument("--processes-from", default=None,
                    help="a text file of command lines to use as the live process list (one per line)")
    a = ap.parse_args(argv)
    cases = json.loads(Path(a.cases).read_text(encoding="utf-8"))
    procs = None
    if a.processes_from:
        procs = [ln for ln in Path(a.processes_from).read_text(encoding="utf-8").splitlines() if ln.strip()]
    rep = run_cases(cases, allow_live=a.allow_live, processes=procs)
    for r in rep["results"]:
        print(f"{r['label']}: {r['status']}" + (f" ({r['reason']})" if r.get("reason") else ""))
    print(f"killed {rep['killed']} of {rep['cases']}; restored byte-identical: {rep['restored_all']}"
          + (f"; LIVE READERS OVERRIDDEN: {list(rep['live_readers_overridden'])}" if rep["live_readers_overridden"] else ""))
    if a.out:
        Path(a.out).write_text(json.dumps(rep, indent=2), encoding="utf-8")
    return 0 if (rep["killed"] == rep["cases"] and rep["restored_all"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
