"""Fidelity check for a REWRITE of a governing document - by machine, never by
having read the source (B3096 / L869 / CHECKLIST #321).

MEASURED 2026-09-24 (session transcript): a 634-line part of the optimisation
runbook's restructure was written 12-15 minutes after the whole 4,301-line
source had been read in the SAME context, and it still (1) switched a HALT
condition the source had left to the owner, (2) dropped two passages tests
pin and split a third across lines, and (3) dropped a check list and a
known-gap note. Reading the source
first did not prevent any of it. A comparison after drafting catches all of
it, so this script is that comparison, for any rewrite:

  1. CITATION COVERAGE - every B / L / S6 / # / test / script token of the old
     text must appear in the new text or a companion (--also), unless the
     --accept file names it WITH A REASON.
  2. RESERVATION CONTINUITY - every old SENTENCE carrying an owner reservation
     or a prohibition (RESERVED_PHRASES) needs a counterpart sentence in the
     new text that carries the same phrase and keeps at least --min-overlap of
     the old sentence's content words. These are the sentences whose loss
     changes WHO DECIDES WHAT: the HALT switch dropped "changing the
     concurrency conclusion is an owner call", and no citation check sees
     that, because the draft kept every citation around it. Each unmatched
     sentence prints with a 10-hex key.

--accept FILE takes "<key-or-token> <reason>" lines for what was retired on
purpose, so the review is recorded and re-runnable; a line with no reason is
REFUSED (exit 2) - an acceptance with no reason is the bare-boolean escape
L789 refuses elsewhere. An accepted key that no longer matches anything is
reported as STALE, so the file cannot quietly outlive the text it excuses.

Generated appendices repeat headings and would mask a drop, so --stop-old /
--stop-new cut each text at the first line starting with a given prefix.

Exit 1 when anything is missing or unmatched, else 0; --report-only exits 0.

    python scripts/doc_rewrite_coverage.py --old archive/<dir>/PLAN.md \\
        --new PLAN.md --also LOG.md --stop-old "## APPENDIX L" \\
        --stop-new "## APPENDIX M" [--accept accepted.txt] [--json out.json]
"""
import argparse
import hashlib
import io
import json
import re
import sys

TOKEN = re.compile(
    r"(?<![A-Za-z0-9-])(S6-B\d{3,4}[a-z]?(?:\.[a-z])?|B\d{3,4}[a-z]?|L\d{2,3}"
    r"|#\d{2,3}|test_b\d{3,4}[a-z0-9_]*|scripts/[A-Za-z0-9_]+\.py"
    r"|[A-Za-z0-9_]+\.py)(?![A-Za-z0-9])")

# Owner reservations first, then prohibitions. Matched case-insensitively on
# whitespace-normalised sentences, so a phrase wrapped across a line break
# still counts (a line-based grep read "owner approval" as dropped when the
# rewrite had only re-wrapped it).
RESERVED_PHRASES = (
    "owner call", "owner's word", "owner-gated", "owner decision",
    "owner approval", "owner ruling", "needs the owner",
    "owner's explicit word", "one-way door", "never auto",
    "do not", "must not", "never")

_STOP = frozenset((
    "the", "and", "for", "not", "are", "was", "were", "has", "have", "had",
    "its", "it's", "this", "that", "with", "from", "into", "but", "any",
    "all", "one", "per", "each", "who", "what", "which", "when", "than",
    "then", "there", "their", "they", "them", "can", "will", "would",
    "only", "also", "our", "out", "been", "does", "did", "via", "own"))
_WORD = re.compile(r"[a-z0-9_][a-z0-9_.'-]*[a-z0-9_]|[a-z0-9]")
_UNIT_START = re.compile(r"(- |\* |\d+\. |\|)")
_SENT_SPLIT = re.compile(r"(?<=[.!?;])\s+(?=[A-Z*`(\"'_\[])")


def load(path: str, stop: str = "") -> str:
    """The file's text, cut at the first line starting with `stop`."""
    text = io.open(path, encoding="utf-8").read().replace("\r\n", "\n")
    if stop:
        lines = text.split("\n")
        for i, ln in enumerate(lines):
            if ln.startswith(stop):
                return "\n".join(lines[:i])
    return text


def tokens(text: str) -> dict:
    """Citation token -> first line number it appears on."""
    out = {}
    for n, ln in enumerate(text.split("\n"), 1):
        for m in TOKEN.finditer(ln):
            tok = m.group(1)
            if tok.startswith("scripts/"):
                tok = tok[len("scripts/"):]
            out.setdefault(tok, n)
    return out


def has_token(text: str, tok: str) -> bool:
    return re.search(r"(?<![A-Za-z0-9-])%s(?![A-Za-z0-9])" % re.escape(tok),
                     text) is not None


def units(text: str) -> list:
    """Paragraphs, list items, table rows and headings, each on one line.
    Blockquote markers are dropped first so a quoted paragraph stays whole."""
    out, cur = [], []
    for raw in text.split("\n"):
        s = re.sub(r"^(\s*>)+\s?", "", raw).strip()
        if not s or s.startswith("#") or _UNIT_START.match(s):
            if cur:
                out.append(" ".join(cur))
                cur = []
            if not s:
                continue
            if s.startswith("#") or s.startswith("|"):
                out.append(s)
                continue
        cur.append(s)
    if cur:
        out.append(" ".join(cur))
    return out


def sentences(text: str) -> list:
    out = []
    for u in units(text):
        out.extend(x.strip() for x in _SENT_SPLIT.split(u) if x.strip())
    return out


def words(s: str) -> set:
    return {w for w in _WORD.findall(s.lower()) if len(w) > 2 and w not in _STOP}


def key(sentence: str) -> str:
    return hashlib.sha1(" ".join(sentence.split()).encode("utf-8")).hexdigest()[:10]


def reserved(sents) -> list:
    """(phrase, sentence) for every sentence carrying a reserved phrase."""
    out = []
    for s in sents:
        low = " ".join(s.lower().split())
        for p in RESERVED_PHRASES:
            if p in low:
                out.append((p, s))
    return out


def check(old: str, new: str, *, min_overlap: float = 0.5,
          accepted=None) -> dict:
    accepted = accepted or {}
    used = set()
    missing = []
    for t, ln in sorted(tokens(old).items()):
        if has_token(new, t):
            continue
        if t in accepted:
            used.add(t)
            continue
        missing.append((t, ln))
    by_phrase = {}
    for p, s in reserved(sentences(new)):
        by_phrase.setdefault(p, []).append(words(s))
    unmatched, seen = [], set()
    for p, s in reserved(sentences(old)):
        k = key(s)
        if (k, p) in seen:
            continue
        seen.add((k, p))
        if k in accepted:
            used.add(k)
            continue
        w = words(s)
        best = 0.0
        if w:
            for c in by_phrase.get(p, ()):
                best = max(best, len(w & c) / len(w))
                if best >= min_overlap:
                    break
        else:
            best = 1.0 if by_phrase.get(p) else 0.0
        if best < min_overlap:
            unmatched.append({"key": k, "phrase": p, "best_overlap": round(best, 2),
                              "sentence": " ".join(s.split())[:400]})
    stale = sorted(k for k in accepted if k not in used)
    return {"missing_tokens": [{"token": t, "old_line": ln} for t, ln in missing],
            "unmatched_reserved": unmatched,
            "accepted_used": sorted(used),
            "accepted_stale": stale,
            "ok": not missing and not unmatched and not stale}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--also", action="append", default=[],
                    help="companion file that received moved text (repeatable)")
    ap.add_argument("--stop-old", default="")
    ap.add_argument("--stop-new", default="")
    ap.add_argument("--min-overlap", type=float, default=0.5)
    ap.add_argument("--accept", help="file of '<key-or-token> <reason>' lines")
    ap.add_argument("--json", help="write the full result here")
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args(argv)
    accepted = {}
    if a.accept:
        for ln in io.open(a.accept, encoding="utf-8"):
            parts = ln.strip().split(None, 1)
            if parts and not parts[0].startswith("#"):
                if len(parts) < 2:
                    print("REFUSED: accepted key %s carries no reason" % parts[0])
                    return 2
                accepted[parts[0]] = parts[1]
    old = load(a.old, a.stop_old)
    new = "\n".join([load(a.new, a.stop_new)] + [load(p) for p in a.also])
    res = check(old, new, min_overlap=a.min_overlap, accepted=accepted)
    print("citation tokens missing: %d" % len(res["missing_tokens"]))
    for m in res["missing_tokens"]:
        print("  MISSING %-36s old line %d" % (m["token"], m["old_line"]))
    print("reserved sentences unmatched: %d (accepted and used: %d)"
          % (len(res["unmatched_reserved"]), len(res["accepted_used"])))
    for u in res["unmatched_reserved"]:
        print("  UNMATCHED %s [%s] overlap %.2f: %s"
              % (u["key"], u["phrase"], u["best_overlap"], u["sentence"][:220]))
    for k in res["accepted_stale"]:
        print("  STALE ACCEPTANCE %s - matches nothing now; remove it" % k)
    if a.json:
        io.open(a.json, "w", encoding="utf-8").write(json.dumps(res, indent=1))
    print("RESULT:", "PASS" if res["ok"] else "FAIL")
    return 0 if (res["ok"] or a.report_only) else 1


if __name__ == "__main__":
    sys.exit(main())
