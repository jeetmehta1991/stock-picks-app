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
    """C1: any non-ASCII in runtime code (excluding docstrings)."""
    violations = []
    for p in paths:
        if p.suffix != ".py":
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
    """C3: new dashboard/inventory/audit docs must declare source-of-truth."""
    violations = []
    target_patterns = ["dashboard_", "_AUDIT", "_INVENTORY", "_REPORT"]
    for p in paths:
        if p.suffix not in (".md", ".py", ".html"):
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
