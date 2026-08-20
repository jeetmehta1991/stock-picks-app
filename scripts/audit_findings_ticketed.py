#!/usr/bin/env python
"""Every FINDING stated in recent turns, checked against EXECUTION_QUEUE.md.

B1712. Two earlier attempts at this audit were weaker than the question asked:
the first checked only the 3 turns since the last commit, the second checked
tickets-per-BATCH and could not see a turn that raised three findings and wrote
one ticket. Both were disclosed as partial. This reads the TRANSCRIPT.

The transcript is ~566 MB / 120k lines, so it is read from the TAIL by byte
offset rather than streamed from the start.

A "finding" here is any assistant sentence carrying remediation or defect
language - the same markers CHECKLIST #225 names. The script extracts them,
then greps EXECUTION_QUEUE.md for corroborating terms.

IMPORTANT - what this can and cannot do:
  CAN  surface every candidate finding sentence, so none is invisible.
  CAN  tell you which have NO plausible queue corroboration at all.
  CANNOT judge whether a matched ticket actually COVERS the finding. That is
        judgment and stays with the reader.
A match here means "something in the queue mentions these terms", not "this is
handled" - reporting it as the latter would be the fail-open this audit exists
to close.

HAND-RUN-ONLY: nothing invokes this automatically (CHECKLIST #224).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "EXECUTION_QUEUE.md"

STOP = {"which", "there", "would", "should", "because", "every", "this", "that",
        "still", "about", "their", "these", "those", "where", "while", "being",
        "built", "remains", "pipeline", "thing", "after", "before", "could",
        # B1712b: the MARKER vocabulary itself. These words are what makes a
        # sentence look like a finding, so they appear all over the queue and can
        # never distinguish one finding from another. Leaving them in is how the
        # first matcher corroborated nonsense.
        "unresolved", "started", "wired", "remediation", "enforced", "mechanical",
        "defect", "breach", "silently", "overridden", "wrong", "never", "inert",
        "cannot", "queue", "ticket", "ticketed", "finding", "findings", "owner",
        "checklist", "gates", "measured", "verified", "session", "turns"}

MARKERS = (
    "not built", "not started", "not wired", "not done", "remediation:",
    "the fix is", "needs a ", "is not enforced", "no mechanical", "not yet built",
    "this is a bug", "is a defect", "root cause", "p0 bug", "breach",
    "silently overrid", "does not exist", "was wrong", "i was wrong",
    "never ran", "inert", "unresolved", "still open", "cannot fire",
)
# Sentences that are quoting the RULE rather than stating a finding.
NOISE = ("checklist #", "learnings l", "| **s6-b", "retroactive coverage")


def tail_entries(path: pathlib.Path, mb: int) -> list[dict]:
    """Parse only the last `mb` megabytes; the head is old turns."""
    size = path.stat().st_size
    start = max(0, size - mb * 1024 * 1024)
    out = []
    with path.open("rb") as fh:
        fh.seek(start)
        if start:
            fh.readline()                      # discard the partial line
        for raw in fh:
            try:
                out.append(json.loads(raw.decode("utf-8", "replace")))
            except Exception:
                continue
    return out


def assistant_text(entries: list[dict]) -> list[str]:
    texts = []
    for d in entries:
        if d.get("type") != "assistant":
            continue
        msg = d.get("message") or {}
        for blk in msg.get("content") or []:
            if isinstance(blk, dict) and blk.get("type") == "text":
                texts.append(blk.get("text") or "")
    return texts


def findings(texts: list[str]) -> list[str]:
    seen, out = set(), []
    for t in texts:
        for line in t.splitlines():
            low = line.lower().strip()
            if len(low) < 30 or any(n in low for n in NOISE):
                continue
            if any(m in low for m in MARKERS):
                key = re.sub(r"[^a-z0-9 ]", "", low)[:90]
                if key not in seen:
                    seen.add(key)
                    out.append(line.strip())
    return out



def _word_in(word: str, text: str) -> bool:
    """True only when `word` appears as a WHOLE WORD in `text`.

    B1772. Substring containment is the recurring matcher defect in this repo:
    `#246` ("free" matched inside "freely" and blocked a clean turn), the B1769
    queue-placeholder check ("-" matched any reason containing a hyphen), and
    this function's own `w in queue`. Underscores count as word characters so
    `smc_breaker` does not match inside `smc_breaker_block`.
    """
    import re as _re
    return _re.search(rf"(?<![A-Za-z0-9_]){_re.escape(word)}(?![A-Za-z0-9_])",
                      text) is not None

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--tail-mb", type=int, default=40)
    ap.add_argument("--show", type=int, default=60)
    a = ap.parse_args()

    entries = tail_entries(pathlib.Path(a.transcript), a.tail_mb)
    texts = assistant_text(entries)
    found = findings(texts)
    queue = QUEUE.read_text(encoding="utf-8", errors="replace").lower()
    # Word frequency across the findings themselves, used to rank rarity: a word
    # appearing in many findings is boilerplate, not an identifier.
    corpus_freq: dict[str, int] = {}
    for f in found:
        for w in set(re.findall(r"[a-z_]{5,}", f.lower())):
            corpus_freq[w] = corpus_freq.get(w, 0) + 1

    uncorroborated = []
    for f in found:
        # 3+ distinctive words from the finding must co-occur in the queue
        # B1712 FIX. The first version counted how many 5+ letter words of the
        # finding appear anywhere in the queue, and a 12,000-line queue contains
        # most common English words - a synthetic finding of pure nonsense
        # ("zebra pipeline quantum flange ... xylophone") scored 5 hits and
        # passed. It corroborated ANYTHING, so its clean result measured nothing.
        # Caught by CHECKLIST #226: feed the check a case it MUST reject.
        #
        # Corroboration now rests on the finding's RAREST informative token -
        # the word that actually identifies it. If that word is absent from the
        # queue, nothing in the queue is plausibly about this finding.
        words = [w for w in re.findall(r"[a-z_]{5,}", f.lower())
                 if w not in STOP]
        if not words:
            continue
        rare = sorted(set(words), key=lambda w: (corpus_freq.get(w, 0), -len(w)))[:3]
        # B1712c: require a MAJORITY of the rare tokens, not merely one. `w in
        # queue` is substring containment, so a single accidental match (a short
        # token living inside a longer word) was enough to suppress the flag -
        # synthetic nonsense scored 1 of 3 and passed. 2 of 3 separates it from a
        # real finding, which scores 3 of 3.
        # B1772: WORD-BOUNDARY, not substring containment. Raising the
        # threshold from 1-of-3 to 2-of-3 (B1712c) REDUCED this defect without
        # removing it - two short tokens living inside longer words still
        # corroborate a finding that the queue never mentions. `w in queue` is
        # the same shape as #246 ("free" matching inside "freely") and as the
        # B1769 placeholder check that blocked its own author.
        hits = sum(1 for w in rare if _word_in(w, queue))
        if hits < 2:
            uncorroborated.append((f"{hits}/3 [{', '.join(rare)}]", f))

    print(f"=== FINDING AUDIT (B1712) ===")
    print(f"  entries parsed (tail {a.tail_mb} MB): {len(entries)}")
    print(f"  assistant text blocks:                {len(texts)}")
    print(f"  candidate finding sentences:          {len(found)}")
    print(f"  WITHOUT queue corroboration:          {len(uncorroborated)}")
    print(f"\n--- uncorroborated (showing {min(a.show, len(uncorroborated))}) ---")
    for rare, f in uncorroborated[: a.show]:
        print(f"  [rare: {rare}] {f[:180]}")
    print("\nNOTE: a corroborated finding is NOT proven handled - the queue merely "
          "mentions its terms. Judging coverage stays with the reader.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
