#!/usr/bin/env python
"""B1778: DONE is self-reported. CLOSED is verified against code and git.

OWNER RULING 2026-08-20: *"Done isn't closure. Closed is only to be marked once
you have verified their work against the actual code and code log and not on
documentation which is highly likely to be incorrect."*

This applies that ruling to the existing ledger. It reads the verdicts from
`audit_done_claims.py` - which joins ticket -> batch -> commit -> files changed,
never the ticket's own prose - and rewrites each terminal row:

    CODE_BACKED     -> CLOSED   the batch commit changed real code
    ANALYSIS_ONLY   -> DONE     self-reported and honest, but NOT code-verified,
                                so under the ruling it CANNOT be CLOSED
    UNSUPPORTED     -> OPEN     claims code; the batch commit shows none
    NO_COMMIT       -> OPEN     no commit exists under that batch number

**DONE stops being terminal.** A DONE row now means "I reported this finished
and nothing has verified it against code". That is the honest reading, and it
is why the open count will RISE sharply - 152 analysis rows move from
"finished" to "unverified". Reporting that rise as a regression would be the
same category-to-claim error that produced "271 closed".

NO NEW CLASSES ARE INVENTED. `CLOSED` is the owner's word; everything else uses
the vocabulary already ruled in B1769. `OPEN` rows written here carry a reason
naming the evidence gap, per `#249`.

HAND-RUN:  python scripts/promote_verified_closed.py [--write]
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "EXECUTION_QUEUE.md"

ROW = re.compile(
    r"^(\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*\*)([A-Z-]+)(\*\*\s*\|\s*)(\S*)(\s*\|)(.*)$")
LIVE = ("OPEN", "BLOCKED", "DEFERRED", "RUNNING")

REASONS = {
    "UNSUPPORTED": ("claims code, but the batch commit touched no code file. "
                    "The work may have landed in another batch - trace it"),
    "NO_COMMIT": ("no commit exists under this batch number, so the DONE claim "
                  "has nothing to verify against - trace or reclassify"),
}


def load_audit():
    spec = importlib.util.spec_from_file_location(
        "adc", ROOT / "scripts" / "audit_done_claims.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    bc = m.batch_commits()
    tests = m.test_names()
    q = QUEUE.read_text(encoding="utf-8")
    seq = collections.defaultdict(list)
    for line in q.splitlines():
        mm = m.ROW.match(line)
        if mm:
            seq[mm.group(1)].append((mm.group(2), mm.group(4)))
    cache: dict[str, list[str]] = {}
    verdicts: dict[str, str] = {}
    for tid, hist in seq.items():
        n = re.match(r"S6-B(\d+)", tid)
        if not n:
            continue
        n = int(n.group(1))
        cls, desc = hist[-1]
        if cls in LIVE:
            continue
        sha = (bc.get(n) or (None, None))[0]
        if sha and sha not in cache:
            cache[sha] = m.files_of(sha)
        files = cache.get(sha, [])
        code = [f for f in files if f.startswith(m.CODE_DIRS)
                and f.endswith(m.CODE_EXT) and not f.endswith(".md")]
        low = re.sub(r"[*_`]", "", desc).lower()
        cc = any(v in low for v in m.CODE_VERBS)
        ca = any(v in low for v in m.ANALYSIS_VERBS)
        if not sha:
            verdicts[tid] = "NO_COMMIT"
        elif code:
            verdicts[tid] = "CODE_BACKED"
        elif cc and not ca:
            verdicts[tid] = "UNSUPPORTED"
        else:
            verdicts[tid] = "ANALYSIS_ONLY"
    return verdicts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    verdicts = load_audit()
    text = QUEUE.read_text(encoding="utf-8")
    out, moved = [], collections.Counter()
    seen_last: dict[str, int] = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = ROW.match(line)
        if m:
            seen_last[m.group(2)] = i

    for i, line in enumerate(lines):
        m = ROW.match(line)
        if not m or seen_last.get(m.group(2)) != i:
            out.append(line)
            continue
        tid, cls, tail = m.group(2), m.group(3), m.group(7)
        v = verdicts.get(tid)
        # B1778b: DROPPED is a DECISION not to do the work, so there is nothing
        # to verify. The dry run tried to promote 4 DROPPED rows to CLOSED on
        # code evidence from their batch - evidence that belongs to OTHER rows
        # in the same commit. Promoting them would have manufactured completion
        # for work deliberately abandoned.
        if cls in LIVE or cls == "DROPPED" or v is None:
            out.append(line)
            continue
        if v == "CODE_BACKED":
            new_cls, extra = "CLOSED", ""
        elif v == "ANALYSIS_ONLY":
            new_cls, extra = "DONE", ""
        else:
            new_cls = "OPEN"
            extra = f" _reason:_ {REASONS[v]}."
        moved[f"{cls}->{new_cls} ({v})"] += 1
        out.append(f"{m.group(1)}{new_cls}{m.group(4)}{m.group(5)}{m.group(6)}"
                   f"{extra}{tail}")

    print("RECLASSIFICATION under the owner ruling (DONE != CLOSED)\n")
    for k, n in sorted(moved.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>4}  {k}")
    print(f"\n  {sum(moved.values())} terminal rows rewritten")
    print("\n  DONE now means SELF-REPORTED AND UNVERIFIED, so the open count")
    print("  RISES. That is the ruling working, not a regression.")

    if a.write:
        QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")
        print("\nWRITTEN")
    else:
        print("\nDRY RUN - pass --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
