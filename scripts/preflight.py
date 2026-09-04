"""scripts/preflight.py - external verification gate.

Pass 53 Day-9 v8h+1 owner-mandated 2026-05-08: replace prose-table
self-graded pre-flight with externally-verifiable script.

Checks the most-violated rules:
  C1: Unicode in non-docstring runtime code (CHECKLIST #75 strict;
      6 violations this session: prefetch_quiver/indices/benzinga/alfred/
      finnhub/build_dashboard).
  C2: Em-dash specifically in scripts/*.py (most common offender).
  C3: Canonical-source declaration in new docs/dashboards (CHECKLIST #77
      violation: dashboard sourced from filesystem instead of inventory).
  C4: prefetch scripts use git_commit_paths() pattern (INV-041 - all-staged
      capture).
  C5: All scripts in scripts/prefetch_*.py are listed in
      scripts/build_dashboard_sprint0a.py ENDPOINTS or CATALOG_ONLY (so
      dashboard reflects the canonical set).

Exit code:
  0 = clean (proceed)
  1 = violation found (BLOCK)

Run modes:
  python scripts/preflight.py                       # check whole repo
  python scripts/preflight.py --staged              # check only git-staged files
  python scripts/preflight.py --paths file1 file2   # check specific files
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_RE = re.compile(r'(\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')', re.MULTILINE)


def get_staged_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        return [REPO_ROOT / line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def runtime_text(source: str) -> str:
    """Return source with docstrings removed (only runtime-printable code)."""
    parts = DOC_RE.split(source)
    return "".join(parts[i] for i in range(0, len(parts), 2))


def check_unicode_in_runtime(paths: Iterable[Path]) -> list[str]:
    """C1: any non-ASCII in runtime code (excluding docstrings).

    Skips vendored/** because that source is upstream we don't control
    (per DEC-045 fork-first architecture); upstream maintainers' use of
    em-dashes/etc. in comments is out of scope for our project's rule.
    """
    violations = []
    for p in paths:
        if p.suffix != ".py":
            continue
        if "vendored" in p.parts:
            continue
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        runtime = runtime_text(text)
        bad = sorted({c for c in runtime if ord(c) > 127 and c not in ("\n", "\r", "\t")})
        if bad:
            codepoints = [hex(ord(c)) for c in bad]
            rel = p.relative_to(REPO_ROOT) if p.is_absolute() else p
            violations.append(
                f"C1 UNICODE | {rel}: non-ASCII codepoints {codepoints} in runtime code "
                f"(use chr(0xN) or ASCII equivalent; emoji/em-dash/arrows banned)"
            )
    return violations


def check_em_dash_in_scripts(paths: Iterable[Path]) -> list[str]:
    """C2: em-dash specifically in scripts/*.py (most common offender)."""
    violations = []
    em_dash = chr(0x2014)
    for p in paths:
        if p.suffix != ".py":
            continue
        if "scripts" not in p.parts:
            continue
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        runtime = runtime_text(text)
        if em_dash in runtime:
            rel = p.relative_to(REPO_ROOT) if p.is_absolute() else p
            violations.append(
                f"C2 EM-DASH | {rel}: contains em-dash (0x2014) in runtime code; "
                f"replace with hyphen-minus '-'"
            )
    return violations


def check_canonical_source_declared(paths: Iterable[Path]) -> list[str]:
    """C3: new dashboard/inventory/audit docs must declare source-of-truth.

    Excludes archive/** paths per owner directive 2026-05-28 (archived
    auto-generated reports are point-in-time snapshots; canonical-source
    declarations don't apply). Mirrors the archive/** exclusion already
    in feedback_all_docs_sweep + L143 per-turn doc-sync rule.
    """
    violations = []
    target_patterns = ["dashboard_", "_AUDIT", "_INVENTORY", "_REPORT"]
    for p in paths:
        if p.suffix not in (".md", ".py", ".html"):
            continue
        # Skip archived snapshots (owner directive 2026-05-28)
        parts = p.parts
        if "archive" in parts:
            continue
        name = p.name.lower()
        if not any(pat.lower() in name for pat in target_patterns):
            continue
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8")[:4000]
        except Exception:
            continue
        # Check for canonical-source declaration markers
        markers = ["source of truth", "source_of_truth", "canonical source",
                    "per CHECKLIST #77", "per CHECKLIST #76", "probe-grounded",
                    "API_ENDPOINT_INVENTORY.md", "PROBE_REPORT"]
        if not any(m.lower() in text.lower() for m in markers):
            rel = p.relative_to(REPO_ROOT) if p.is_absolute() else p
            violations.append(
                f"C3 CANONICAL-SOURCE | {rel}: no declaration of source-of-truth in first 4000 chars; "
                f"add '# Source: <URL or path>' or 'per CHECKLIST #77' near top"
            )
    return violations


def check_prefetch_scripts_use_path_restricted_commit(paths: Iterable[Path]) -> list[str]:
    """C4: prefetch scripts must use `git commit -- <paths>` not bare git commit
    (INV-041 fix - prevents capturing all staged files)."""
    violations = []
    for p in paths:
        if p.suffix != ".py":
            continue
        name = p.name
        if not name.startswith("prefetch_"):
            continue
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        # Look for git_commit-like helpers that DON'T use --
        if 'subprocess.run(["git", "commit"' in text or "subprocess.run(['git', 'commit'" in text:
            # Check if any commit invocation lacks `--`
            commit_calls = re.findall(r'subprocess\.run\(\s*\[["\']git["\']\s*,\s*["\']commit["\'][^\]]*\]', text)
            risky = [c for c in commit_calls if '"--"' not in c and "'--'" not in c]
            if risky:
                rel = p.relative_to(REPO_ROOT) if p.is_absolute() else p
                violations.append(
                    f"C4 GIT-COMMIT-CAPTURE | {rel}: git commit invocation without '--' path "
                    f"separator captures all staged files (INV-041); use git_commit_paths() pattern"
                )
    return violations


def get_staged_added_lines() -> list[tuple[str, str]]:
    """Return (file, added_line) pairs from the staged diff (B1254 C7)."""
    try:
        # B1298: explicit utf-8 decode with replacement -- on Windows the
        # default cp1252 text decode CRASHES the whole preflight when the
        # staged diff contains any multi-byte char (emoji in a doc), which
        # blocked a legitimate commit. Gates must not be DoS-able by docs.
        # B2581 (L756): --ignore-cr-at-eol, same reason as the orphan-rule gate -
        # a line-ending flip would present an entire file as newly added and the
        # C7 banned-pattern scan would run over all of it.
        result = subprocess.run(
            ["git", "diff", "--cached", "-U0", "--ignore-cr-at-eol",
             "--diff-filter=ACMR"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
            encoding="utf-8", errors="replace",
        )
    except Exception:
        return []
    if result.stdout is None:
        return []
    pairs = []
    current = ""
    for line in result.stdout.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            pairs.append((current, line[1:]))
    return pairs


def check_pyramid_stamp(paths: Iterable[Path]) -> list[str]:
    """C6 (B1254, S6-B1253-GATE-A1; B1267 owner decision 2a 2026-07-08):
    EVERY commit requires an existing GREEN full-pyramid stamp
    (feedback_pyramid_no_exceptions -- no doc/data carve-outs; the
    pre-B1267 py-only scope codified exactly the carve-out the standing
    rule rejects, L206 drift #2). Commits staging *.py additionally
    require the stamp be FRESHER than the newest staged .py mtime.
    Stamp written by backtest/tests/conftest.py pytest_sessionfinish
    only when BOTH tiers ran and passed.
    """
    import json
    staged_any = [p for p in paths if p.exists()]
    if not staged_any:
        return []
    py_staged = [p for p in staged_any if p.suffix == ".py"
                 and ("backtest" in p.parts or "scripts" in p.parts)
                 and "vendored" not in p.parts and "tests" not in p.parts]
    stamp_path = REPO_ROOT / ".pyramid_stamp"
    if not stamp_path.exists():
        return ["C6 PYRAMID-STAMP | no .pyramid_stamp; every commit requires "
                "a green full pyramid (owner decision 2a, B1267); run "
                "test_unit.py + test_integration.py first"]
    try:
        stamp = json.loads(stamp_path.read_text(encoding="utf-8"))
    except Exception:
        return ["C6 PYRAMID-STAMP | .pyramid_stamp unreadable; re-run the full pyramid"]
    if not stamp.get("green"):
        return ["C6 PYRAMID-STAMP | last full-pyramid run was RED; fix tests before commit"]
    stamp_ts = float(stamp.get("timestamp", 0))
    stale = [str(p.relative_to(REPO_ROOT)) for p in py_staged
             if p.stat().st_mtime > stamp_ts]
    if stale:
        return [f"C6 PYRAMID-STAMP | staged .py modified AFTER last green pyramid: "
                f"{stale[:5]}; re-run the full pyramid"]
    return []


# C7 banned patterns: (rule-id, compiled regex, path-scope substring, message)
_BANNED_LINE_PATTERNS = [
    ("C7a NOT-S-GET", re.compile(r"not\s+s\.get\("), "backtest/signals/",
     "banned `not s.get(...)` gate (feedback_never_use_NOT_s_get_pattern); "
     "use the positive symmetric producer signal"),
    ("C7b DEFAULT-TRUE-GATE", re.compile(r"s\.get\(\s*['\"][a-z0-9_]+['\"]\s*,\s*True\s*\)"),
     "backtest/signals/",
     "default-True strategy gate auto-passes on missing producer key "
     "(B657/W6-W8 silent-gap class); default False or add producer"),
    ("C7c RELATIVE-PREFETCH-PATH", re.compile(r"Path\(\s*['\"]data_prefetch"), "backtest/",
     "cwd-sensitive relative data_prefetch path (B1250 ENG-8); "
     "anchor via Path(__file__)"),
]


def check_banned_patterns_in_staged_diff() -> list[str]:
    """C7 (B1254, S6-B1253-GATE-A2): scan ADDED lines in the staged diff
    for known bug-class patterns. Waiver: `# preflight-allow: <rule>` on
    the same line (auditable in the diff itself).
    """
    violations = []
    for fname, line in get_staged_added_lines():
        if "preflight-allow" in line:
            continue
        if fname.startswith("backtest/tests/") or fname.startswith("scripts/preflight"):
            continue
        for rule_id, pattern, scope, msg in _BANNED_LINE_PATTERNS:
            if scope not in fname.replace("\\", "/"):
                continue
            if pattern.search(line):
                violations.append(f"{rule_id} | {fname}: {msg} | line: {line.strip()[:90]}")
    # C7d: except Exception followed immediately by bare pass/return-empty
    pairs = get_staged_added_lines()
    for i in range(len(pairs) - 1):
        f1, l1 = pairs[i]
        f2, l2 = pairs[i + 1]
        if f1 != f2 or not f1.replace("\\", "/").startswith("backtest/"):
            continue
        if f1.startswith("backtest/tests/"):
            continue
        if "preflight-allow" in l1 or "preflight-allow" in l2:
            continue
        if re.search(r"except\s+Exception\s*:?\s*$", l1.strip()) and \
                l2.strip() in ("pass", "return {}", "return None", "continue"):
            violations.append(
                f"C7d SILENT-SWALLOW | {f1}: `except Exception` + bare "
                f"`{l2.strip()}` without logging (CHECKLIST #122); pair with a "
                f"logger call or `# preflight-allow: C7d` with justification")
    return violations


_BATCH_CLAIM_RX = re.compile(
    r"BATCH[ _-]?(\d+)[^\n]{0,60}?(COMPLETE|PASS\b|SUCCESS)", re.IGNORECASE)


def find_unbacked_batch_claims(added_lines, has_outputs_fn) -> list[str]:
    """C10 core (B1337, CHECKLIST #160 companion): a queue line CLAIMING a
    batch complete requires that batch's outputs tracked in the repo
    (output_batches/batch_<N>/). Pure function for testability;
    has_outputs_fn(n) -> bool. Waiver: `preflight-allow: C10` on the line.
    Batch-1 lineage: batch-1 outputs sat only in S3+temp for a full day
    (B1334 miss) -- CSV-first requires results in-repo.
    """
    violations = []
    seen = set()
    for fname, line in added_lines:
        if not fname.replace("\\", "/").endswith("EXECUTION_QUEUE.md"):
            continue
        if "preflight-allow" in line:
            continue
        for m in _BATCH_CLAIM_RX.finditer(line):
            n = int(m.group(1))
            # queue batch-numbering (B1234...) is 4-digit; run batches are small
            if n > 500 or n in seen:
                continue
            seen.add(n)
            if not has_outputs_fn(n):
                violations.append(
                    f"C10 BATCH-OUTPUTS | queue claims batch {n} "
                    f"{m.group(2).upper()} but output_batches/batch_{n}/ has no "
                    f"tracked/staged files (CSV-first; commit the cube CSV + "
                    f"fingerprint + trade_log, or waive with "
                    f"`preflight-allow: C10`)")
    return violations



def check_arbitrary_selection_declared() -> list[str]:
    """C11 (B1446, owner directive: "No arbitrary decisions. That's an absolute red flag").

    Scan ADDED lines in the staged diff for CONVENIENCE-DEFAULT selection idioms --
    picking a winner by size, order, or first match -- and require the enclosing hunk to
    carry either a justification marker or an explicit ARBITRARY-PENDING-JUSTIFICATION
    label. A number published from an unjustified selection rule carries authority the
    method does not have (CHECKLIST #165).

    Lineage: B1444 de-duplication chose each cluster's survivor by LARGEST TRADE SET --
    a size heuristic with no performance basis -- while the canonical pipeline uses
    eigenvalue effective-N. Six strategies were nearly decommissioned on it.

    Waiver: in-hunk "# selection-justified: <measured basis>" or
    "ARBITRARY-PENDING-JUSTIFICATION".
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--unified=3", "--", "*.py"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        diff = result.stdout
    except Exception:
        return []
    if not diff:
        return []
    idioms = [
        (re.compile(r"sorted\([^)]*key\s*=\s*lambda[^)]*:\s*-?len\("), "sorted-by-size"),
        (re.compile(r"\.idxmax\(\)|\.idxmin\(\)"), "argmax/argmin selection"),
        (re.compile(r"max\([^)]*key\s*=\s*len|min\([^)]*key\s*=\s*len"), "max/min-by-length"),
    ]
    waivers = ("selection-justified", "ARBITRARY-PENDING-JUSTIFICATION")
    violations: list[str] = []
    hunk: list[str] = []
    added: list[str] = []

    def flush() -> None:
        blob = "\n".join(hunk)
        if any(w in blob for w in waivers):
            return
        for line in added:
            for pat, label in idioms:
                if pat.search(line):
                    violations.append(
                        "C11 ARBITRARY-SELECTION | " + label + " with no stated basis | "
                        + line.strip()[:80]
                        + " | add '# selection-justified: <measured basis>' or "
                        "'ARBITRARY-PENDING-JUSTIFICATION' + ticket (CHECKLIST #165)"
                    )
                    return

    for line in diff.splitlines():
        if line.startswith("@@"):
            flush()
            hunk, added = [], []
        hunk.append(line)
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    flush()
    return violations

def check_batch_outputs_committed() -> list[str]:
    """C10 wrapper: staged-diff added lines + git-index lookup."""
    def has_outputs(n: int) -> bool:
        res = subprocess.run(
            ["git", "ls-files", "--cached", f"output_batches/batch_{n}/"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
            encoding="utf-8", errors="replace")
        return bool((res.stdout or "").strip())
    return find_unbacked_batch_claims(get_staged_added_lines(), has_outputs)


def check_queue_entry_staged() -> list[str]:
    """C8 (B1254, S6-B1253-GATE-A3): every commit must stage
    EXECUTION_QUEUE.md (CHECKLIST #94 queue-anchor rule) OR set env
    GIT_QUEUE_EXEMPT=1 (exemption appended to .queue_exempt_log so
    every bypass is auditable).
    """
    import os
    import time as _t
    _res = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        encoding="utf-8", errors="replace",
    )
    staged = (_res.stdout or "").splitlines()
    staged = [s.strip().replace("\\", "/") for s in staged if s.strip()]
    if not staged:
        return []
    if any(s.endswith("EXECUTION_QUEUE.md") for s in staged):
        return []
    if os.environ.get("GIT_QUEUE_EXEMPT") == "1":
        try:
            with open(REPO_ROOT / ".queue_exempt_log", "a", encoding="utf-8") as fh:
                fh.write(f"{_t.strftime('%Y-%m-%dT%H:%M:%S')} exempt commit staging: "
                         f"{staged[:10]}\n")
        except Exception:
            pass
        return []
    return ["C8 QUEUE-ENTRY | commit does not stage EXECUTION_QUEUE.md "
            "(CHECKLIST #94 queue-anchor). Add the batch entry, or set "
            "GIT_QUEUE_EXEMPT=1 for a logged exemption (pure formatting/"
            "revert commits only)"]


_TICKET_ID_RE = re.compile(r"\bS\d+-B\d{3,4}-[A-Z0-9][A-Z0-9-]+\b")


def check_doc_ticket_ids_in_queue(paths: Iterable[Path]) -> list[str]:
    """C9 (B1255, S6-B1253-GATE-A4): every ticket-ID pattern mentioned in a
    staged output_audit/*.md doc must exist in EXECUTION_QUEUE.md (working
    copy). Findings-without-tickets-don't-exist, mechanically enforced
    (L205; the B1251 gap class).
    """
    queue_path = REPO_ROOT / "EXECUTION_QUEUE.md"
    try:
        queue_text = queue_path.read_text(encoding="utf-8")
    except Exception:
        return ["C9 DOC-QUEUE-XCHECK | EXECUTION_QUEUE.md unreadable"]
    violations = []
    for p in paths:
        if p.suffix != ".md" or "output_audit" not in p.parts or not p.exists():
            continue
        if "archive" in p.parts:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        ids = sorted(set(_TICKET_ID_RE.findall(text)))
        missing = [t for t in ids if t not in queue_text]
        if missing:
            rel = p.relative_to(REPO_ROOT) if p.is_absolute() else p
            violations.append(
                f"C9 DOC-QUEUE-XCHECK | {rel}: ticket IDs referenced but absent "
                f"from EXECUTION_QUEUE.md: {missing[:8]} (queue-anchor rule; "
                f"add tickets before committing the doc)")
    return violations



# C12 (S6-B1534a, B1808): an L-number must identify ONE lesson.
#
# MEASURED at B1808: FOUR numbers were duplicated - L114 x2, L115 x2, L253 x3,
# L333 x2 - and each pair is a DISTINCT lesson. A citation of "L253" is
# therefore ambiguous among three entries, in a system whose entire discipline
# is built on citing L-numbers.
#
# RATCHET, not a hard block. Failing on the existing four would block every
# commit until they are renumbered, and renumbering means deciding which entry
# keeps the number and rewriting citations across CHECKLIST, SKILL, the queue
# and commit history - a judgment about the historical record that belongs to
# the owner (tracked as S6-B1808b). The baseline below pins the known set so it
# cannot GROW; removing an entry from it is always allowed.
KNOWN_DUPLICATE_L = {"114", "115", "253", "333"}


CRLF = bytes((13, 10))     # B2581: written as ordinals so the
LF = bytes((10,))          # constants survive any transport
CR = bytes((13,))


def check_line_ending_rewrite() -> list[str]:
    """C13 (B2581 / L756): BLOCK a commit that rewrites a file's line endings.

    MEASURED on the B2580 commit: `Path.write_text` on Windows turned every
    bare LF in LEARNINGS.md into CRLF, so a 57-line append staged as 18,868
    added / 18,812 removed - unreviewable, and it made two diff-reading gates
    treat the whole file as new. The signature is a large raw diff whose
    CR-blind counterpart is tiny.
    """
    def _numstat(extra: list[str]) -> dict[str, int]:
        try:
            r = subprocess.run(["git", "diff", "--cached", "--numstat", *extra],
                               cwd=REPO_ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
        except Exception:
            return {}
        out = {}
        for line in (r.stdout or "").splitlines():
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            a, d, name = parts
            if a == "-" or d == "-":      # binary
                continue
            out[name] = int(a) + int(d)
        return out

    def _bare_endings(ref: str, name: str) -> int:
        """How many line endings in a blob are NOT CRLF (bare LF + lone CR).

        This is the quantity a Windows rewrite destroys: `write_text` emits
        CRLF, so a flip drives it to zero and a restore brings it back. The
        direction is what separates the damage from its repair - B2581 shipped
        this as a count of DISTINCT ending KINDS, and the B2582 retro-sweep
        found the hole: CANONICAL_FACTS.md is UNIFORM bare LF (843 lines), so
        flipping the whole file leaves the kind count at 1 -> 1 and the gate
        would have passed the worst instance of the class it exists to catch.
        """
        try:
            r = subprocess.run(["git", "show", ref + ":" + name], cwd=REPO_ROOT,
                               capture_output=True, check=False)
            b = r.stdout or b""
        except Exception:
            return 0
        crlf = b.count(CRLF)
        return (b.count(LF) - crlf) + (b.count(CR) - crlf)

    raw, blind = _numstat([]), _numstat(["--ignore-cr-at-eol"])
    bad = []
    for name, n in sorted(raw.items()):
        m = blind.get(name, 0)
        if n >= 50 and m * 5 < n and \
                _bare_endings(":0", name) < _bare_endings("HEAD", name):
            bad.append(
                f"C13 LINE-ENDING REWRITE (B2581/L756): {name} stages {n} changed "
                f"lines but only {m} survive --ignore-cr-at-eol - the rest is a "
                f"line-ending flip, which is unreviewable and makes every "
                f"diff-reading gate treat the file as new. A patcher must write "
                f"BYTES (or open with newline=''); restore the file from HEAD and "
                f"re-apply the real change.")
    return bad


def check_duplicate_learning_numbers(paths: Iterable[Path],
                                     source: Path | None = None) -> list[str]:
    """C12: no NEW duplicate L-number may be committed.

    Runs only when LEARNINGS.md is staged, which is the only way a duplicate
    can be introduced.

    `source` is injectable so the check can be exercised on a fixture instead of
    on the live file (#241: a check with no seam can only be pinned as
    check([]) == [], which passes for a check wired to nothing).
    """
    import collections
    import re as _re

    if not any(Path(p).name == "LEARNINGS.md" for p in paths):
        return []
    src = source if source is not None else REPO_ROOT / "LEARNINGS.md"
    if not src.exists():
        return []
    nums = _re.findall(r"^### L(\d+)", src.read_text(encoding="utf-8"), _re.M)
    dupes = {n for n, c in collections.Counter(nums).items() if c > 1}
    new = sorted(dupes - KNOWN_DUPLICATE_L, key=int)
    if not new:
        return []
    return [f"C12 | LEARNINGS.md: duplicate L-number(s) {['L' + n for n in new]}. "
            "An L-number must identify ONE lesson - CHECKLIST, SKILL.md, the "
            "queue and commit messages all cite them, and a duplicate makes "
            "every citation ambiguous. Use the next free number "
            f"(highest is currently L{max(int(x) for x in nums)})."]


# C14 (B2608 / L765): drafting markers in an APPEND-ONLY record.
#
# EXECUTION_QUEUE.md is read last-row-wins and never edited in place, so a
# half-thought written into a row is permanent - correcting it costs a SECOND
# row, and until someone reads that far the garbled figure stays quotable.
# MEASURED: `minq8 +0.043... wait, minq8 +0.054` shipped at cd9650a36 and
# needed B2607b to restate the band cleanly.
#
# The marker set is deliberately TINY. A gate over prose earns false positives
# fast, and the cost of one here is a blocked commit on a legitimate row.
_DRAFT_MARKERS = ("... wait", "...wait", " wait, no", " oops", " scratch that",
                  " i mean,", " actually, no")


def _strip_code_spans(text: str) -> str:
    """B1738: vocabulary inside backticks is a MENTION, not a use.

    Without this the gate refuses the very row that RECORDS the defect - the
    self-reference trap this repo has hit repeatedly - so it is built in here
    rather than bolted on after the gate blocks its own incident report.
    """
    return re.sub(r"`[^`]*`", " ", text)


def check_queue_row_is_not_a_draft() -> list[str]:
    """C14: refuse a staged EXECUTION_QUEUE.md row containing a drafting marker."""
    violations = []
    for f, line in get_staged_added_lines():
        if Path(f).name != "EXECUTION_QUEUE.md":
            continue
        stripped = _strip_code_spans(line).lower()
        hits = [m for m in _DRAFT_MARKERS if m in stripped]
        if hits:
            violations.append(
                f"C14 QUEUE-ROW-IS-A-DRAFT | a staged EXECUTION_QUEUE.md row "
                f"carries {hits!r}. The ledger is APPEND-ONLY: a correction "
                f"costs a second row and the garbled text stays quotable until "
                f"someone reads that far (L765). Restate the row before "
                f"committing. Quoting the marker inside `backticks` is a "
                f"mention and is not refused.")
    return violations


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--staged", action="store_true", help="check git-staged files only")
    ap.add_argument("--paths", nargs="+", default=None, help="specific paths to check")
    ap.add_argument("--all", action="store_true", help="check whole repo")
    args = ap.parse_args()

    if args.staged:
        files = get_staged_files()
    elif args.paths:
        files = [Path(p) for p in args.paths]
    elif args.all:
        files = list((REPO_ROOT / "scripts").glob("*.py"))
        files += list(REPO_ROOT.glob("*.md"))
        files += [p for p in (REPO_ROOT / "dashboard_sprint0a").glob("*") if p.is_file()]
    else:
        # Default: staged
        files = get_staged_files()

    if not files:
        print("preflight: no files to check (no staged changes?)")
        return 0

    print(f"preflight: checking {len(files)} file(s)...")
    all_violations = []
    all_violations += check_unicode_in_runtime(files)
    all_violations += check_em_dash_in_scripts(files)
    all_violations += check_canonical_source_declared(files)
    all_violations += check_prefetch_scripts_use_path_restricted_commit(files)
    # B1254 (Council 300, S6-B1253-GATE-A1/A2/A3 owner-approved): the
    # mechanical compliance gates run only in --staged (commit) mode.
    if args.staged or (not args.paths and not args.all):
        all_violations += check_pyramid_stamp(files)
        all_violations += check_banned_patterns_in_staged_diff()
        all_violations += check_queue_entry_staged()
        # B1255 (Council 300, S6-B1253-GATE-A4 owner-approved)
        all_violations += check_doc_ticket_ids_in_queue(files)
        # B1337 (Council 365 owner-approved): C10 batch-complete claims
        # require committed outputs (CSV-first)
        all_violations += check_batch_outputs_committed()
        # B1446 (owner: "No arbitrary decisions"): C11 selection-rule gate
        all_violations += check_arbitrary_selection_declared()
        # C12 (S6-B1534a): no NEW duplicate L-number
        all_violations += check_duplicate_learning_numbers(files)
        # C13 (B2581 / L756): no line-ending rewrite
        all_violations += check_line_ending_rewrite()
        # C14 (B2608 / L765): no drafting marker in an append-only ledger row
        all_violations += check_queue_row_is_not_a_draft()

    if not all_violations:
        print("preflight: PASS - no rule violations found")
        return 0

    print(f"\npreflight: FAIL - {len(all_violations)} violation(s) BLOCK this commit:\n")
    for v in all_violations:
        print(f"  {v}")
    print("\nFix violations and re-run. To bypass (NOT recommended), use git commit --no-verify.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
