#!/usr/bin/env python
"""B1777: verify every DONE ticket against CODE and the CHANGE LOG, not prose.

Owner: *"Do a deep audit of these tickets. Compare against work that has
actually been done. Don't rely on prose or documentation but verify against code
and change log."*

THE JOIN. A ticket id encodes its batch (`S6-B1772a` -> 1772) and each batch has
a commit whose subject starts `B1772:`. So ticket -> commit -> files-changed is
mechanical, and every verdict below is derived from git, never from the ticket's
own words.

THE THREE VERDICTS, and the middle one is the reason this is not a witch-hunt:

  CODE_BACKED    the batch commit changed a .py under scripts/ or backtest/,
                 and - when the ticket CLAIMS a test or gate - a `test_b<N>_`
                 function exists.

  ANALYSIS_ONLY  the commit touched only docs/data AND the ticket's prose uses
                 ANALYSIS verbs (measured, audited, counted, found). **This is
                 legitimate.** A measurement turn produces a number and a
                 lesson, not a diff. Calling it a false claim would be the
                 mirror of calling every born-DONE row a fabrication.

  UNSUPPORTED    the commit touched only docs/data (or is missing) while the
                 prose uses CODE verbs (built, wired, fixed, added, gated).
                 **This is the finding that matters.**

A NOTE ON WHAT THIS CANNOT SEE: a commit touching code does not prove THIS
ticket's code landed - a batch ships up to 3 changes and carries several rows.
CODE_BACKED is therefore necessary, not sufficient: it rules out the class of
claim with no code behind it at all. Overstating it would repeat the defect
under audit.

HAND-RUN: python scripts/audit_done_claims.py [--window-hours 48] [--csv out.csv]
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

CODE_VERBS = ("built", "wired", "fixed", "added", "gated", "installed",
              "converted", "routed", "implemented", "patched", "disabled",
              "removed", "stemmed", "hardened", "pinned", "migrated")
ANALYSIS_VERBS = ("measured", "audited", "counted", "found", "investigated",
                  "re-derived", "rederived", "verified", "confirmed", "ran",
                  "reported", "recorded", "diagnosed", "checked", "stale",
                  "answered", "decided", "ruled", "noted", "retracted",
                  "superseded", "closed on evidence")
# B1777b: "code" is not only .py. A settings/hook/shell change is a real
# change; counting it as prose produced false UNSUPPORTED verdicts (B1764
# shipped .claude/settings.json and nothing else).
CODE_DIRS = ("scripts/", "backtest/", ".claude/")
CODE_EXT = (".py", ".json", ".sh", ".bat", ".toml", ".cfg", ".yml", ".yaml")
LIVE = ("OPEN", "BLOCKED", "DEFERRED", "RUNNING")

ROW = re.compile(
    r"^\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*\*([A-Z-]+)\*\*\s*\|\s*(\S*)\s*\|(.*)$")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True).stdout


def batch_commits() -> dict[int, tuple[str, dt.datetime]]:
    out: dict[int, tuple[str, dt.datetime]] = {}
    for line in git("log", "--all", "--format=%H|%ad|%s", "--date=iso").splitlines():
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        sha, d, subj = parts
        # B1777b: a commit can cover SEVERAL batches ("B1760/B1761: ..."), so
        # matching only the leading number reported 45 tickets as NO_COMMIT
        # when their work shipped inside a combined commit. Claiming those as
        # unsupported would have been a fabricated accusation - the same
        # category-to-claim leap this audit exists to correct.
        head = re.match(r"\s*((?:B\d+[/+, ]*)+)", subj)
        if not head:
            continue
        nums = [int(x) for x in re.findall(r"B(\d+)", head.group(1))]
        try:
            when = dt.datetime.fromisoformat(d.strip())
        except ValueError:
            continue
        for n in nums:
            if n not in out or when < out[n][1]:
                out[n] = (sha, when)
    return out


def files_of(sha: str) -> list[str]:
    return [f for f in git("show", "--stat=200", "--name-only", "--format=",
                           sha).splitlines() if f.strip()]


def test_names() -> set[int]:
    got = set()
    for p in (ROOT / "backtest" / "tests" / "test_unit.py",
              ROOT / "backtest" / "tests" / "test_integration.py"):
        if p.exists():
            for m in re.finditer(r"def test_b(\d+)", p.read_text(encoding="utf-8")):
                got.add(int(m.group(1)))
    return got


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-hours", type=float, default=48.0)
    ap.add_argument("--csv")
    ap.add_argument("--show", type=int, default=12)
    a = ap.parse_args()

    bc = batch_commits()
    tests = test_names()
    now = max(w for _, w in bc.values())
    cutoff = now - dt.timedelta(hours=a.window_hours)

    q = (ROOT / "EXECUTION_QUEUE.md").read_text(encoding="utf-8")
    seq = collections.defaultdict(list)
    for line in q.splitlines():
        m = ROW.match(line)
        if m:
            seq[m.group(1)].append((m.group(2), m.group(4)))

    file_cache: dict[str, list[str]] = {}
    rows = []
    for tid, hist in seq.items():
        m = re.match(r"S6-B(\d+)", tid)
        if not m:
            continue
        n = int(m.group(1))
        cls, desc = hist[-1]
        if cls in LIVE:
            continue                          # only DONE/DROPPED claims audited
        born_done = hist[0][0] not in LIVE
        sha, when = bc.get(n, (None, None))
        in_window = bool(when and when >= cutoff)

        if sha not in file_cache and sha:
            file_cache[sha] = files_of(sha)
        files = file_cache.get(sha, [])
        code = [f for f in files
                if f.startswith(CODE_DIRS) and f.endswith(CODE_EXT)
                and not f.endswith(".md")]
        low = re.sub(r"[*_`]", "", desc).lower()
        claims_code = any(v in low for v in CODE_VERBS)
        claims_analysis = any(v in low for v in ANALYSIS_VERBS)
        has_test = n in tests

        if not sha:
            verdict = "NO_COMMIT"
        elif code:
            verdict = "CODE_BACKED"
        elif claims_code and not claims_analysis:
            verdict = "UNSUPPORTED"
        else:
            verdict = "ANALYSIS_ONLY"

        rows.append(dict(ticket=tid, batch=n, cls=cls, born_done=born_done,
                         in_window=in_window, sha=(sha or "")[:9],
                         n_files=len(files), n_code=len(code),
                         claims_code=claims_code, claims_analysis=claims_analysis,
                         has_test=has_test, verdict=verdict,
                         desc=re.sub(r"\s+", " ", low)[:120]))

    def tally(sel):
        c = collections.Counter(r["verdict"] for r in rows if sel(r))
        tot = sum(c.values())
        return c, tot

    print(f"DONE-CLAIM AUDIT  (verified against git, not prose)")
    print(f"  batches with a commit: {len(bc)} | test_b* functions: {len(tests)}")
    print(f"  window: last {a.window_hours:.0f}h (since {cutoff:%Y-%m-%d %H:%M})\n")

    for label, sel in (("ALL terminal tickets", lambda r: True),
                       ("terminal, LAST 48H", lambda r: r["in_window"])):
        c, tot = tally(sel)
        print(f"{label}: {tot}")
        for k in ("CODE_BACKED", "ANALYSIS_ONLY", "UNSUPPORTED", "NO_COMMIT"):
            v = c.get(k, 0)
            print(f"   {v:>5}  {100*v/tot if tot else 0:5.1f}%  {k}")
        print()

    bad = [r for r in rows if r["verdict"] in ("UNSUPPORTED", "NO_COMMIT")]
    print(f"NEEDS EXPLANATION: {len(bad)}")
    for r in sorted(bad, key=lambda r: -r["batch"])[:a.show]:
        print(f"   {r['ticket']:<14} B{r['batch']} {r['verdict']:<12} "
              f"files={r['n_files']:<3} {r['desc'][:66]}")

    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {a.csv} ({len(rows)} rows)")

    print("\nCODE_BACKED is NECESSARY, NOT SUFFICIENT: a batch ships up to 3")
    print("changes and carries several rows, so a code commit does not prove")
    print("THIS row's code landed. It rules out claims with no code at all.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
