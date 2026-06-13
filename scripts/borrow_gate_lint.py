# Source: B713 Phase 0 + Decision 3 build #4 + Decision 5 Cat 1 + owner-approved "push forward" 2026-06-13 per CHECKLIST #77
"""B744 borrow-gate lint -- static check that every short-emitting strategy in
`backtest/signals/screener.py` declares an explicit borrow guard at call site.

Per S4-B713-REGISTRATION-TIME-BORROW-GATE-LINT-BUILD: each strategy whose return
path includes direction="short" output (`_strat(..., "short", ...)` OR `_strat3`
with a SHORT branch) must:
  1. Reference `_short_borrow_trap_active(s)` in its function body (the explicit
     borrow gate at the call site).
  2. Declare `"borrow_ok"` in its `signals_used` list passed to `_strat`/`_strat3`.

This complements the per-cohort regression guards in B741/B743 by providing a
single cluster-wide invariant check that runs every pyramid invocation.

Prerequisites met by B740-B743 cohort: all 51 pure-short + 61 dual _strat3
strategies converted to explicit gate.

USAGE
-----
    from scripts.borrow_gate_lint import audit_screener, format_report
    report = audit_screener("backtest/signals/screener.py")
    print(format_report(report))

CLI: `python -m scripts.borrow_gate_lint`

The pyramid pin in `backtest/tests/test_batch744_borrow_gate_lint.py` invokes
this auditor + fails if `report.violations` is non-empty.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path


# --------------------------------------------------------------------------
# Data shapes
# --------------------------------------------------------------------------
@dataclass
class ShortStrategy:
    """One strategy in screener.py whose return path emits direction='short'."""
    name: str
    line: int
    is_dual: bool                  # True if uses _strat3 (long+short); False if pure-short _strat
    has_borrow_gate: bool          # function body references _short_borrow_trap_active(s)
    has_borrow_ok_declared: bool   # signals_used (or signals_used_short) contains "borrow_ok"


@dataclass
class LintReport:
    short_strategies: list = field(default_factory=list)
    violations: list = field(default_factory=list)  # list[ShortStrategy] with missing gate/decl
    files_scanned: int = 0
    note: str = ""


# --------------------------------------------------------------------------
# Static analysis
# --------------------------------------------------------------------------
def _function_bodies(src: str) -> list[tuple[str, int, int, int]]:
    """Return list of (function_name, def_line, body_start, body_end_exclusive).

    Uses ast for accurate function boundaries; falls back to line-walk if ast
    parses but produces no function defs (unlikely).
    """
    tree = ast.parse(src)
    out = []
    lines = src.splitlines()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("strat_"):
            # ast.end_lineno is 1-based; convert to 0-based exclusive end
            start = node.lineno - 1
            end = (node.end_lineno or start + 1)
            out.append((node.name, node.lineno, start, end))
    return out


def _is_short_strategy(body_text: str) -> tuple[bool, bool]:
    """Returns (emits_short, is_dual).

    emits_short:  True if function body has `_strat(*, "short", *)` OR `_strat3(*, *, *, ...)`
    is_dual:      True if uses _strat3 (has both long+short branches)
    """
    # _strat3 indicates a dual strategy; both long+short potentially emit
    has_strat3 = bool(re.search(r"return\s+_strat3\(", body_text))
    # _strat(var, "short", ...) pattern
    has_pure_short = bool(re.search(r'return\s+_strat\([^,]+,\s*"short"', body_text))
    emits_short = has_strat3 or has_pure_short
    return (emits_short, has_strat3)


def _has_explicit_borrow_gate(body_text: str) -> bool:
    """The function body references `_short_borrow_trap_active(s)`."""
    return "_short_borrow_trap_active(s)" in body_text


def _declares_borrow_ok(body_text: str, is_dual: bool) -> bool:
    """The signals_used list (or signals_used_short for _strat3) contains the
    string `"borrow_ok"`.

    For pure-short strategies: any occurrence of "borrow_ok" in the body is
    sufficient (only one signals_used list exists).

    For dual `_strat3` strategies: we need to confirm "borrow_ok" appears in
    `signals_used_short` (the 5th positional arg), NOT in `signals_used_long`.
    Approach: count occurrences -- if "borrow_ok" appears exactly once, it must
    be in the short list (long list is for direction=long). If it appears
    >= 2 times that's a bug (declared on long too); the lint flags via a
    separate check.
    """
    return '"borrow_ok"' in body_text


def _borrow_ok_in_long_branch(body_text: str) -> bool:
    """For dual _strat3 strategies, flag if `borrow_ok` is incorrectly declared
    in the LONG branch signals_used (positional arg 4). The 4th arg is the
    signals_used_long; the 5th is signals_used_short.

    Walk the call-arg tokens like the B742 harness does.
    """
    if "return _strat3(" not in body_text:
        return False
    # find _strat3( position
    s3 = body_text.find("_strat3(")
    if s3 < 0:
        return False
    pos = s3 + len("_strat3")  # at `(`
    depth_paren = 0
    depth_bracket = 0
    arg_index = 0
    in_string = False
    string_char = None
    long_list_start = None
    long_list_end = None
    while pos < len(body_text):
        ch = body_text[pos]
        if in_string:
            if ch == "\\":
                pos += 2
                continue
            if ch == string_char:
                in_string = False
            pos += 1
            continue
        if ch in ('"', "'"):
            in_string = True
            string_char = ch
            pos += 1
            continue
        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
            if depth_paren == 0:
                break
        elif ch == "[":
            depth_bracket += 1
            if depth_paren == 1 and depth_bracket == 1 and arg_index == 3 and long_list_start is None:
                long_list_start = pos
        elif ch == "]":
            depth_bracket -= 1
            if depth_paren == 1 and depth_bracket == 0 and arg_index == 3 and long_list_end is None:
                long_list_end = pos + 1
        elif ch == "," and depth_paren == 1 and depth_bracket == 0:
            arg_index += 1
        pos += 1
    if long_list_start is None or long_list_end is None:
        return False
    long_list_text = body_text[long_list_start:long_list_end]
    return '"borrow_ok"' in long_list_text


def audit_screener(screener_path: str | Path = "backtest/signals/screener.py") -> LintReport:
    path = Path(screener_path)
    if not path.is_file():
        return LintReport(note=f"screener.py not found at {path}")

    src = path.read_text(encoding="utf-8")
    bodies = _function_bodies(src)
    src_lines = src.splitlines()

    rep = LintReport(files_scanned=1)
    for name, lineno, start, end in bodies:
        body_text = "\n".join(src_lines[start:end])
        emits_short, is_dual = _is_short_strategy(body_text)
        if not emits_short:
            continue
        has_gate = _has_explicit_borrow_gate(body_text)
        has_decl = _declares_borrow_ok(body_text, is_dual)
        s = ShortStrategy(
            name=name,
            line=lineno,
            is_dual=is_dual,
            has_borrow_gate=has_gate,
            has_borrow_ok_declared=has_decl,
        )
        rep.short_strategies.append(s)
        # Violation conditions
        if not has_gate or not has_decl:
            rep.violations.append(s)
            continue
        # For dual strategies, also check `borrow_ok` is NOT in long branch
        if is_dual and _borrow_ok_in_long_branch(body_text):
            rep.violations.append(s)
    return rep


def format_report(rep: LintReport) -> str:
    L = [
        f"BORROW-GATE LINT  files={rep.files_scanned}  short_strategies={len(rep.short_strategies)}  violations={len(rep.violations)}",
    ]
    if rep.note:
        L.append(f"  note: {rep.note}")
    L.append("")
    if rep.violations:
        L.append("VIOLATIONS:")
        for v in rep.violations:
            kind = "dual_strat3" if v.is_dual else "pure_short"
            issues = []
            if not v.has_borrow_gate:
                issues.append("missing _short_borrow_trap_active(s) in body")
            if not v.has_borrow_ok_declared:
                issues.append("missing 'borrow_ok' in signals_used")
            L.append(f"  [{kind}] {v.name}  line {v.line}  --  {'; '.join(issues) or 'borrow_ok appears in LONG branch (should be SHORT-only)'}")
    else:
        L.append("OK: every short-emitting strategy declares explicit borrow_ok gate at call site")
    return "\n".join(L)


if __name__ == "__main__":  # pragma: no cover
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "backtest/signals/screener.py"
    rep = audit_screener(target)
    print(format_report(rep))
    sys.exit(0 if not rep.violations else 1)
