"""scripts/triage_quarantine.py (B1474, ticket S6-B1471b) -- classify every QUARANTINE file
by WHY it fails, so 72 unknowns become a closable list.

WHY CLASSIFY RATHER THAN FIX
B1471 fixed one quarantine cluster by hand and found the failures were not one thing. Four files
split into: stale count pins (bookkeeping no batch updated), a REAL compliance gap (three B1382
mirror shorts carrying the borrow gate without declaring `borrow_ok`, unreported for 12 days), and
a lint violation. The prior that "old failing tests are bit-rot" is what kept the real one hidden
(L316, CHECKLIST #180). So the remaining 72 get classified before anyone decides what to do with
them.

CLASSES
  ARTIFACT     needs a generated file/dir absent from the repo (FileNotFoundError, missing output
               dir, empty parquet). Belongs in a tier that SKIPS cleanly rather than errors.
  STALE-PIN    an equality assertion on a count or a name that a later batch changed. Cheap to fix,
               but per CHECKLIST #179 the pin is the LAST thing to change -- confirm the delta's
               cause first.
  COLLECTION   fails at import/collection: a module, fixture or symbol is gone. Usually a rename
               nobody propagated.
  BEHAVIOUR    an assertion about what the code DOES. These are the candidates for real findings
               and get read individually.
  UNKNOWN      no signature matched -- read it.

Each file is run ALONE, so a classification is not contaminated by cross-file pollution (the
S6-B1468a defect). Output is a per-file table plus a JSON ledger for ticketing.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# B1474: pytest-timeout is NOT installed in this environment, so passing --timeout made
# pytest exit with "unrecognized arguments" and run ZERO tests. Both this script and
# bisect_test_polluter.py silently measured nothing until the implausibility of the
# result (72 of 72 identical) exposed it. The subprocess timeout below does the same job
# without depending on a plugin, and _assert_pytest_ran refuses to classify output that
# is not a pytest result (CHECKLIST #174: prove the probe RAN).
def _assert_pytest_ran(out: str, label: str) -> None:
    if "unrecognized arguments" in out or "ERROR: usage:" in out:
        raise SystemExit(
            "[HALT] pytest rejected its arguments while running " + str(label)
            + ": " + out[:300]
            + " -- the probe never executed; any classification would be fiction."
        )

sys.path.insert(0, str(REPO / "backtest" / "tests"))

SIGNATURES = [
    ("ARTIFACT", re.compile(
        r"FileNotFoundError|No such file or directory|does not exist|"
        r"NotADirectoryError|EmptyDataError|No columns to parse|"
        r"Errno 2|missing.*artifact|output.*not found", re.I)),
    ("COLLECTION", re.compile(
        r"ImportError|ModuleNotFoundError|AttributeError: module|"
        r"cannot import name|fixture '.*' not found|ERROR collecting", re.I)),
    ("STALE-PIN", re.compile(
        r"assert \d+ == \d+|expected \d+ .*got \d+|== \d+,\s*f?\"expected|"
        r"not in ALL_STRATEGIES|missing from ALL_STRATEGIES", re.I)),
]


def classify(output: str) -> str:
    for name, pat in SIGNATURES:
        if pat.search(output):
            return name
    if "assert" in output or "AssertionError" in output:
        return "BEHAVIOUR"
    return "UNKNOWN"


def main() -> int:
    import pyramid_tiers as pt

    files = list(pt.QUARANTINE)
    print("=" * 100)
    print(f"QUARANTINE TRIAGE (B1474 / S6-B1471b) -- {len(files)} files, each run ALONE")
    print("=" * 100)

    rows, counts = [], {}
    for i, f in enumerate(files, 1):
        path = f"backtest/tests/{f}"
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", path, "-q", "--tb=short",
                 "-p", "no:randomly"],
                cwd=REPO, capture_output=True, text=True, timeout=300)
            out = r.stdout + r.stderr
            _assert_pytest_ran(out, path)
        except subprocess.TimeoutExpired:
            out, cls = "", "TIMEOUT"
        else:
            cls = "GREEN" if " failed" not in out and " error" not in out.lower() else classify(out)
        counts[cls] = counts.get(cls, 0) + 1
        # first assertion line is the most informative single line
        detail = ""
        for ln in out.splitlines():
            if "Error" in ln or ln.strip().startswith("E "):
                detail = ln.strip()[:110]
                break
        rows.append({"file": f, "class": cls, "detail": detail})
        print(f"  [{i:>2}/{len(files)}] {cls:<11} {f[:58]:<58} {detail[:40]}")

    print("\n" + "=" * 100)
    for k in sorted(counts, key=lambda x: -counts[x]):
        print(f"  {k:<12} {counts[k]:>3}")
    print("=" * 100)

    out_p = REPO / "output_audit" / "b1474_quarantine_triage.json"
    out_p.write_text(json.dumps({"n_files": len(files), "counts": counts, "rows": rows},
                                indent=2), encoding="utf-8")
    print(f"\n[OK] wrote {out_p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
