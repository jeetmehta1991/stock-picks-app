# -*- coding: utf-8 -*-
"""B1787: tickets from the last 48h that claimed to BUILD something - did it land?

Owner: *"In the last 48 hours a lot of tickets were added that were supposed to
build something. So do a recheck and verify in depth."*

THE METHOD. A build claim names a thing. Extract the named artifact from the
ticket text and check it EXISTS in the codebase today - not whether the batch
commit touched some file, which B1777 already showed is the wrong entity (a
batch carries several rows).

Three artifact kinds, each checkable exactly:
    scan_/check_ gate   -> defined in verify_turn_compliance.py AND referenced
    test_bNNN_          -> defined in a test file
    scripts/*.py        -> the file exists

Anything else is NOT_CHECKABLE and is reported as such rather than guessed.
B1779 measured that inferring "symbols" from free prose yields ~100pct false
positives, so this only trusts the three shapes above.
"""
import collections
import datetime as dt
import io
import pathlib
import re
import subprocess

ROOT = pathlib.Path(r"c:\Users\jeetm\Github\stock-picks-app")
ROW = re.compile(
    r"^\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*\*([A-Z-]+)\*\*\s*\|\s*(\S*)\s*\|(.*)$")

# batch -> earliest commit date
log = subprocess.run(["git", "log", "--all", "--format=%ad|%s", "--date=iso"],
                     cwd=ROOT, capture_output=True, text=True).stdout
bd = {}
for line in log.splitlines():
    if "|" not in line:
        continue
    d, subj = line.split("|", 1)
    for n in re.findall(r"B(\d+)", re.match(r"\s*((?:B\d+[/+, ]*)+)", subj).group(1)
                        if re.match(r"\s*((?:B\d+[/+, ]*)+)", subj) else ""):
        n = int(n)
        try:
            w = dt.datetime.fromisoformat(d.strip())
        except ValueError:
            continue
        if n not in bd or w < bd[n]:
            bd[n] = w
if not bd:
    raise SystemExit("no batch commits parsed")
cutoff = max(bd.values()) - dt.timedelta(hours=48)
recent = {n for n, w in bd.items() if w >= cutoff}

# the live artifact inventory
vtc = (ROOT / "scripts" / "verify_turn_compliance.py").read_text(encoding="utf-8")
gates = set(re.findall(r"def (scan_\w+|check_\w+)", vtc))
wired = {g for g in gates if len(re.findall(rf"\b{re.escape(g)}\b", vtc)) > 1}
tests = set()
for tf in (ROOT / "backtest" / "tests").glob("test_*.py"):
    tests |= set(re.findall(r"def (test_\w+)", tf.read_text(encoding="utf-8",
                                                            errors="replace")))
# B1787c: the inventory globbed scripts/ ONLY, so backtest/run_phase1a.py
# and backtest/tests/test_unit.py read as MISSING. Every one of the 4
# missing verdicts was my inventory, not the ticket.
scripts = {p.name for p in (ROOT / "scripts").glob("*.py")}
scripts |= {p.name for p in (ROOT / "backtest").rglob("*.py")}

BUILD = ("built", "wired", "added", "gated", "implemented", "installed",
         "converted", "routed", "pinned", "shipped", "created")

q = io.open(ROOT / "EXECUTION_QUEUE.md", encoding="utf-8").read()
latest = {}
for line in q.splitlines():
    m = ROW.match(line)
    if m:
        latest[m.group(1)] = (m.group(2), m.group(3), m.group(4))

rows = []
for tid, (cls, prio, desc) in sorted(latest.items()):
    b = re.match(r"S6-B(\d+)", tid)
    if not b or int(b.group(1)) not in recent:
        continue
    # B1787b: strip PAIRED markdown emphasis only. Stripping bare _ removed
    # the underscore from every snake_case identifier, so no artifact could
    # ever match and the script reported 0 LANDED / 17 MISSING - all false.
    # A suspiciously clean result is a bug in the harness until proven.
    low = re.sub(r"\*\*?", "", desc).lower()
    if not any(v in low for v in BUILD):
        continue
    named_gates = set(re.findall(r"\b((?:scan|check)_[a-z0-9_]+)", low))
    named_tests = set(re.findall(r"\b(test_b\w+)", low))
    named_scripts = set(re.findall(r"\b([a-z0-9_]+\.py)\b", low))
    checks, missing = [], []
    for g in named_gates:
        (checks if g in gates else missing).append(f"gate:{g}")
        if g in gates and g not in wired:
            missing.append(f"gate-not-wired:{g}")
    for t in named_tests:
        (checks if t in tests else missing).append(f"test:{t}")
    for sc in named_scripts:
        (checks if sc in scripts else missing).append(f"script:{sc}")
    if not checks and not missing:
        verdict = "NOT_CHECKABLE"
    elif missing:
        verdict = "MISSING"
    else:
        verdict = "LANDED"
    rows.append((tid, cls, verdict, sorted(checks)[:3], sorted(missing)[:3],
                 re.sub(r"\s+", " ", low)[:70]))

c = collections.Counter(r[2] for r in rows)
print(f"tickets from the last 48h claiming to BUILD: {len(rows)}")
for k in ("LANDED", "MISSING", "NOT_CHECKABLE"):
    print(f"  {c.get(k,0):>4}  {k}")
print()
miss = [r for r in rows if r[2] == "MISSING"]
print(f"MISSING ({len(miss)}) - the artifact the ticket NAMES is absent or unwired:")
for tid, cls, v, ok, bad, d in miss:
    print(f"  {tid:<14} {cls:<9} {','.join(bad)[:56]:<56} {d[:44]}")
print()
print(f"NOT_CHECKABLE: {c.get('NOT_CHECKABLE',0)} tickets claim a build but name no")
print("gate, test or script - they cannot be verified mechanically at all.")
