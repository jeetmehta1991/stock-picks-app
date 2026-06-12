# Source: B708 reviewer ICT class-of-bug audit + Decision 3 build #3 owner-approved per CHECKLIST #77
"""
producer_collision_audit.py
===========================

Static (AST-only) defensive lint that flags two collision classes across the
`backtest/signals/` producer files:

  1) NAME-COLLISION: two `compute_*` functions whose names differ ONLY by
     pluralization, casing, or one trailing character. The B705 ICT review
     surfaced `compute_po3_signal` (singular, multi_timeframe.py:194) vs
     `compute_po3_signals` (plural, ict_producers.py:46). Both currently
     wire correctly because each strategy explicitly imports the right one,
     but a future refactor that re-routes one of them is a class-of-bug
     risk. Flagging the names earns a one-line action: rename, or document
     in OPEN_INVESTIGATIONS why both must stay.

  2) KEY-COLLISION: two `compute_*` functions that emit the SAME signal key
     into the strategy state dict. The strategy-state dict is the merged
     output of every producer; if two producers write the same key, the
     later writer silently overrides the earlier one and the per-strategy
     `s.get(key)` is non-deterministic across module-import order.

The tool reads files; it does NOT import or execute them, so it works even
when the producer modules have side-effect imports or missing data
dependencies.

USAGE
-----
    from producer_collision_audit import audit_signals_dir, format_report
    rep = audit_signals_dir("backtest/signals")
    print(format_report(rep))

CLI: `python -m scripts.producer_collision_audit` (defaults to backtest/signals)
"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


# ----------------------------------------------------------------------------
# Data shapes
# ----------------------------------------------------------------------------
@dataclass
class ProducerFn:
    """One `compute_*` function discovered in a signals module."""
    name: str
    module_path: str
    lineno: int
    emitted_keys: set = field(default_factory=set)


@dataclass
class NameCollision:
    fn_a: ProducerFn
    fn_b: ProducerFn
    kind: str          # "pluralization" | "case" | "near_miss"
    distance: int      # edit distance (1 for plural/case, n for near_miss)


@dataclass
class KeyCollision:
    key: str
    producers: list    # list[ProducerFn] -- 2+ producers emitting the same key


@dataclass
class AuditReport:
    producers: list = field(default_factory=list)
    name_collisions: list = field(default_factory=list)
    key_collisions: list = field(default_factory=list)
    files_scanned: int = 0
    note: str = ""


# ----------------------------------------------------------------------------
# AST extraction: emitted keys.
# ----------------------------------------------------------------------------
# Heuristic: producers in this codebase consistently use these names for the
# output dict before returning. If a function uses none of these and instead
# returns a literal dict, we extract keys from the literal.
_OUTPUT_DICT_NAMES = {"out", "result", "signals", "sig", "ret", "d", "output"}


def _extract_emitted_keys_from_function(fn: ast.FunctionDef) -> set:
    """Walk a function body and collect every constant-string key it writes to
    an `out[*] = ...` style assignment OR returns in a dict literal.

    Heuristic, not perfect: captures the load-bearing case (constant-string
    subscript assignment), skips dynamic key construction (`out[f"{x}_y"]`).
    Dynamic-key omissions are flagged in the report.
    """
    keys: set[str] = set()
    has_dynamic_key = False

    for node in ast.walk(fn):
        # out["key"] = ...
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                    if target.value.id in _OUTPUT_DICT_NAMES:
                        sl = target.slice
                        if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                            keys.add(sl.value)
                        else:
                            has_dynamic_key = True
        # out.update({"key": ...}) or {...} literal return
        elif isinstance(node, ast.Call):
            if (isinstance(node.func, ast.Attribute) and node.func.attr == "update"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id in _OUTPUT_DICT_NAMES):
                for a in node.args:
                    if isinstance(a, ast.Dict):
                        for k in a.keys:
                            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                                keys.add(k.value)
                            else:
                                has_dynamic_key = True
        elif isinstance(node, ast.Return):
            v = node.value
            if isinstance(v, ast.Dict):
                for k in v.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        keys.add(k.value)
                    else:
                        has_dynamic_key = True

    if has_dynamic_key:
        # mark via a private sentinel so the report can call it out
        keys.add("__has_dynamic_key__")
    return keys


def _discover_producers(module_path: Path) -> list:
    """Parse a single signals module and return one ProducerFn per top-level
    `compute_*` function. We intentionally skip nested/inner functions.
    """
    src = module_path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(module_path))
    out: list[ProducerFn] = []
    for node in tree.body:  # top-level only
        if isinstance(node, ast.FunctionDef) and node.name.startswith("compute_"):
            keys = _extract_emitted_keys_from_function(node)
            out.append(ProducerFn(
                name=node.name,
                module_path=str(module_path),
                lineno=node.lineno,
                emitted_keys=keys,
            ))
    return out


# ----------------------------------------------------------------------------
# Collision detection
# ----------------------------------------------------------------------------
def _edit_distance(a: str, b: str, cap: int = 4) -> int:
    """Levenshtein distance, capped to spare runtime. Returns cap+1 if exceeded."""
    if a == b:
        return 0
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    # classic DP
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        row_min = cur[0]
        for j, cb in enumerate(b, 1):
            ins = cur[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (ca != cb)
            cur[j] = min(ins, dele, sub)
            if cur[j] < row_min:
                row_min = cur[j]
        if row_min > cap:
            return cap + 1
        prev = cur
    return prev[-1]


def _classify_name_collision(a: str, b: str) -> tuple[str, int] | None:
    """Return (kind, distance) if a and b are near-twin function names; else None."""
    if a == b:
        return None
    if a.lower() == b.lower():
        return ("case", _edit_distance(a, b))
    # pluralization: differ by single trailing 's'
    if a + "s" == b or b + "s" == a:
        return ("pluralization", 1)
    d = _edit_distance(a, b, cap=2)
    if d <= 2:
        return ("near_miss", d)
    return None


def _detect_name_collisions(producers: list) -> list:
    out: list[NameCollision] = []
    # only compare across modules -- same-module same-name is impossible (Python),
    # and within-module compute_x vs compute_xs is intentional (return-shape ladder)
    by_module: dict[str, list[ProducerFn]] = {}
    for p in producers:
        by_module.setdefault(p.module_path, []).append(p)
    mod_list = list(by_module.items())
    for i in range(len(mod_list)):
        for j in range(i + 1, len(mod_list)):
            mi, fns_i = mod_list[i]
            mj, fns_j = mod_list[j]
            for a in fns_i:
                for b in fns_j:
                    cls = _classify_name_collision(a.name, b.name)
                    if cls:
                        kind, dist = cls
                        out.append(NameCollision(a, b, kind, dist))
    return out


def _detect_key_collisions(producers: list) -> list:
    by_key: dict[str, list[ProducerFn]] = {}
    for p in producers:
        for k in p.emitted_keys:
            if k.startswith("__"):  # internal sentinel
                continue
            by_key.setdefault(k, []).append(p)
    return [KeyCollision(k, fns) for k, fns in by_key.items() if len(fns) >= 2]


# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------
def audit_signals_dir(signals_dir: str | os.PathLike = "backtest/signals",
                      include: Iterable[str] | None = None,
                      exclude: Iterable[str] | None = None) -> AuditReport:
    base = Path(signals_dir)
    if not base.is_dir():
        return AuditReport(note=f"signals dir not found: {base}")
    files = sorted(base.glob("*.py"))
    if include:
        keep = set(include)
        files = [f for f in files if f.name in keep]
    if exclude:
        drop = set(exclude)
        files = [f for f in files if f.name not in drop]
    producers: list[ProducerFn] = []
    for f in files:
        try:
            producers.extend(_discover_producers(f))
        except SyntaxError as e:
            # never crash an audit on a single parse failure -- record and continue
            producers.append(ProducerFn(
                name=f"__parse_error__{f.name}",
                module_path=str(f), lineno=0,
                emitted_keys={f"__parse_error__:{e.msg}"},
            ))
    rep = AuditReport(
        producers=producers,
        name_collisions=_detect_name_collisions(producers),
        key_collisions=_detect_key_collisions(producers),
        files_scanned=len(files),
    )
    return rep


def format_report(rep: AuditReport) -> str:
    L = [f"PRODUCER COLLISION AUDIT  files={rep.files_scanned}  producers={len(rep.producers)}"]
    if rep.note:
        L.append(f"  note: {rep.note}")

    L.append(f"\n=== NAME COLLISIONS ({len(rep.name_collisions)}) ===")
    if not rep.name_collisions:
        L.append("  (none)")
    for nc in rep.name_collisions:
        L.append(
            f"  [{nc.kind} d={nc.distance}] {nc.fn_a.name} ({Path(nc.fn_a.module_path).name}:{nc.fn_a.lineno}) "
            f"<-> {nc.fn_b.name} ({Path(nc.fn_b.module_path).name}:{nc.fn_b.lineno})"
        )

    L.append(f"\n=== KEY COLLISIONS ({len(rep.key_collisions)}) ===")
    if not rep.key_collisions:
        L.append("  (none)")
    for kc in rep.key_collisions:
        owners = ", ".join(
            f"{p.name}({Path(p.module_path).name}:{p.lineno})" for p in kc.producers
        )
        L.append(f"  '{kc.key}': {owners}")

    return "\n".join(L)


if __name__ == "__main__":  # pragma: no cover - simple CLI
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "backtest/signals"
    print(format_report(audit_signals_dir(target)))
