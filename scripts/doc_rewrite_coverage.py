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
  3. FIGURE CONTEXT (S6-B3096h, B3107) - every number-with-unit of the old
     text (hours, minutes, seconds, GB/MB/KB, pct, bps, dollars, an
     attached multiplier like 2.8x) counts as CARRIED only where a new
     sentence holds the same value AND keeps at least --min-overlap of the
     content words beside it in the old sentence (FIGURE_CONTEXT a side).
     MEASURED at B3096: an ad-hoc value probe run beside this CLI passed a
     dropped cost row, '100 tickers x 1003 days (4y) ~= 7.3 h', because
     7.3 h also sits in an unrelated sentence of the new runbook - a
     value-only presence test passes on a coincidence. An uncarried figure
     whose value survives elsewhere prints VALUE ELSEWHERE: that is the
     coincidence shape. A shared-unit list or range ('2.0 / 2.1 / 4.0 h')
     yields one figure per value; a heading id such as 11.2s is a section,
     not 11.2 seconds; '41 x 20' is multiplication, not a multiplier.

--accept FILE takes "<key-or-token> <reason>" lines for what was retired on
purpose, so the review is recorded and re-runnable; a line with no reason is
REFUSED (exit 2) - an acceptance with no reason is the bare-boolean escape
L789 refuses elsewhere. An accepted key that no longer matches anything is
reported as STALE, so the file cannot quietly outlive the text it excuses.

Generated appendices repeat headings and would mask a drop, so --stop-old /
--stop-new cut each text at the first line starting with a given prefix.

Exit 1 when anything is missing, unmatched or uncarried, else 0; --report-only
exits 0.

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


# S6-B3096h (B3107): the FIGURES leg - see item 3 of the docstring.
# a thousands comma only when a DIGIT follows it (B3107: "2026-08-23, second"
# had read as 23 + comma + a unit)
_NUM = r"\d(?:\d|,(?=\d))*(?:\.\d+)?"
_FIG_UNITS = r"h|hrs?|hours?|min|minutes?|s|secs?|seconds?|ms|gb|mb|kb|tb|pct|%|bps"
FIGURE = re.compile(
    r"(?<![\w.$/\u00a7-])(?:"
    r"\$\s?(?P<money>" + _NUM + r")(?![\d.])"
    r"|(?P<vals>" + _NUM + r"(?:\s*[-/]\s*" + _NUM + r")*)\s?"
    r"(?P<unit>" + _FIG_UNITS + r")(?![\w-])"
    r"|(?P<mult>" + _NUM + r")x(?![\w-]))", re.I)
FIGURE_CONTEXT = 3
_DATE = re.compile(r"\d{4}-\d{1,2}(?:-\d{1,2})?")
_FIG_UNIT = {"hr": "h", "hrs": "h", "hour": "h", "hours": "h",
             "minute": "min", "minutes": "min", "sec": "s", "secs": "s",
             "second": "s", "seconds": "s", "%": "pct"}
_SECTION_ID = re.compile(r"^#+\s+(?:\u00a7|SS)?(\d+(?:\.\d+)+[a-z]\w*)", re.M)


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


def figures(sentence: str, section_ids=frozenset()) -> list:
    """(figure, start, end) for every figure in a sentence. A shared-unit
    list or range yields one figure per value, so a new '2.0 / 2.1 / 4.0 h'
    carries an old '2.0 h'; a match equal to a heading id (11.2s) is a
    section reference and is skipped."""
    out = []
    for m in FIGURE.finditer(sentence):
        if m.group("money"):
            out.append(("$" + m.group("money").replace(",", ""), m.start(), m.end()))
        elif m.group("mult"):
            out.append((m.group("mult").replace(",", "") + "x", m.start(), m.end()))
        else:
            if m.group(0).replace(" ", "").lower() in section_ids:
                continue
            # a DATE followed by a unit-shaped word ("2026-08-23 second
            # message") is not a range of seconds - measured: 3 of the 25
            # figures first flagged on the B3096 pair were this shape.
            if _DATE.fullmatch(m.group("vals").replace(" ", "")):
                continue
            unit = m.group("unit").lower()
            unit = _FIG_UNIT.get(unit, unit)
            for v in re.split(r"\s*[-/]\s*", m.group("vals")):
                out.append((v.replace(",", "") + " " + unit, m.start(), m.end()))
    return out


def _content_words(text: str) -> list:
    return [w for w in _WORD.findall(text.lower()) if len(w) > 2 and w not in _STOP]


def figure_context(sentence: str, start: int, end: int) -> set:
    """The FIGURE_CONTEXT nearest content words on each side of a figure,
    inside its sentence - what a coincidental occurrence elsewhere lacks."""
    # other figures are dropped from the context: "4.2h" and "4.2 h" tokenise
    # differently, so keeping them scored a carried sentence on formatting.
    left, right = FIGURE.sub(" ", sentence[:start]), FIGURE.sub(" ", sentence[end:])
    return (set(_content_words(left)[-FIGURE_CONTEXT:])
            | set(_content_words(right)[:FIGURE_CONTEXT]))


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
        w = words(s)
        best = 0.0
        if w:
            for c in by_phrase.get(p, ()):
                best = max(best, len(w & c) / len(w))
                if best >= min_overlap:
                    break
        else:
            best = 1.0 if by_phrase.get(p) else 0.0
        if best >= min_overlap:
            continue          # carried: an acceptance for it would be STALE (B3107)
        if k in accepted:
            used.add(k)
            continue
        if best < min_overlap:
            unmatched.append({"key": k, "phrase": p, "best_overlap": round(best, 2),
                              "sentence": " ".join(s.split())[:400]})
    # S6-B3096h: the figures leg, anchored on context (docstring item 3).
    ids = {i.lower() for i in _SECTION_ID.findall(old + "\n" + new)}
    index = {}
    for s in sentences(new):
        found = figures(s, ids)
        if found:
            ws = words(s)
            for f, _a, _b in found:
                index.setdefault(f, []).append(ws)
    uncarried, fseen = [], set()
    for s in sentences(old):
        for f, a, b in figures(s, ids):
            k = key(f + "|" + s)
            if k in fseen:
                continue
            fseen.add(k)
            ctx = figure_context(s, a, b)
            cands = index.get(f, ())
            if ctx:
                best = max((len(ctx & w) / len(ctx) for w in cands), default=0.0)
            else:
                best = 1.0 if cands else 0.0
            if best >= min_overlap:
                continue      # carried: an acceptance for it would be STALE
            if k in accepted:
                used.add(k)
                continue
            if best < min_overlap:
                uncarried.append({"key": k, "figure": f, "best_overlap": round(best, 2),
                                  "value_elsewhere": bool(cands),
                                  "sentence": " ".join(s.split())[:400]})
    stale = sorted(k for k in accepted if k not in used)
    return {"missing_tokens": [{"token": t, "old_line": ln} for t, ln in missing],
            "unmatched_reserved": unmatched,
            "uncarried_figures": uncarried,
            "figures_checked": len(fseen),
            "accepted_used": sorted(used),
            "accepted_stale": stale,
            "ok": not missing and not unmatched and not uncarried and not stale}


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
    # B3107: a sentence carrying a character outside the console code page
    # (U+2248 on a cp1252 console) crashed the report mid-list - measured on
    # the B3096 pair. Replace it in the PRINTED report; the --json keeps it.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
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
    print("figures uncarried: %d of %d" % (len(res["uncarried_figures"]),
                                           res["figures_checked"]))
    for u in res["uncarried_figures"]:
        print("  UNCARRIED %s [%s] overlap %.2f%s: %s"
              % (u["key"], u["figure"], u["best_overlap"],
                 " VALUE ELSEWHERE" if u["value_elsewhere"] else "",
                 u["sentence"][:220]))
    for k in res["accepted_stale"]:
        print("  STALE ACCEPTANCE %s - matches nothing now; remove it" % k)
    if a.json:
        io.open(a.json, "w", encoding="utf-8").write(json.dumps(res, indent=1))
    print("RESULT:", "PASS" if res["ok"] else "FAIL")
    return 0 if (res["ok"] or a.report_only) else 1


if __name__ == "__main__":
    sys.exit(main())
