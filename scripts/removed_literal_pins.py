"""Pins on text a change REMOVES (L939, CHECKLIST #315).

A change's selector names the pins it breaks (#315). The pins easiest to miss
are the ones that never name the thing changed: a test that greps a source
file for a string literal - test_b2904 found the soldiers' RSI bound by
quoting a signals_used annotation, and S6-B3139c replaced the annotation with
the exact key. Twice in one session (L938, L939) the search for broken pins
keyed on the concept being edited and the full gate found the pin instead.

This lists, for every changed .py file, the string constants present in the
committed version and absent from the working copy (AST constants, so a
literal that merely MOVED within the file is not reported), and every test or
script file that quotes one of them. It is advisory - a hit can be a test
that legitimately names the old text - and runs in seconds, so it belongs
BEFORE the gate, not instead of it.

    python scripts/removed_literal_pins.py             # working tree vs HEAD
    python scripts/removed_literal_pins.py --min-len 4

Pinned by test_b3139c_removed_literal_pins_finds_a_test_quoting_removed_text.
"""
import argparse
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEARCH_GLOBS = ("backtest/tests/*.py", "scripts/*.py")


def string_constants(text: str) -> set:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    return {n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def removed_literals(old_text: str, new_text: str, min_len: int = 3) -> set:
    """String constants in old_text that new_text no longer holds."""
    return {s for s in string_constants(old_text) - string_constants(new_text)
            if len(s) >= min_len and "\n" not in s}


def quoting_hits(literals, files) -> list:
    """(file, line, literal) for every file quoting a removed literal."""
    hits = []
    for f in files:
        try:
            text = Path(f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lit in sorted(literals):
            for q in (f'"{lit}"', f"'{lit}'"):
                i = text.find(q)
                if i >= 0:
                    hits.append((str(f), text[:i].count("\n") + 1, lit))
                    break
    return hits


def _changed_py(root: Path) -> list:
    out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "*.py"],
                         cwd=str(root), capture_output=True, text=True, check=True).stdout
    return [p for p in out.split() if p]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--min-len", type=int, default=3)
    a = ap.parse_args(argv)
    changed = _changed_py(ROOT)
    files = sorted({p for g in SEARCH_GLOBS for p in ROOT.glob(g)})
    total = 0
    for rel in changed:
        path = ROOT / rel
        old = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                             capture_output=True, text=True).stdout
        new = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        gone = removed_literals(old, new, a.min_len)
        hits = [h for h in quoting_hits(gone, files) if Path(h[0]).resolve() != path.resolve()]
        total += len(hits)
        print(f"{rel}: {len(gone)} string constants removed; {len(hits)} quoted elsewhere")
        for f, ln, lit in hits:
            print(f"  {Path(f).relative_to(ROOT).as_posix()}:{ln}  {lit!r}")
    print(f"changed .py files {len(changed)}; files searched {len(files)}; hits {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
