import ast, sys
from pathlib import Path

def assigned_names(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                for x in ast.walk(t):
                    if isinstance(x, ast.Name):
                        out.add(x.id)
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
            if isinstance(n.target, ast.Name):
                out.add(n.target.id)
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            for x in ast.walk(n.target):
                if isinstance(x, ast.Name):
                    out.add(x.id)
        elif isinstance(n, ast.withitem) and n.optional_vars is not None:
            for x in ast.walk(n.optional_vars):
                if isinstance(x, ast.Name):
                    out.add(x.id)
    return out

def loads_in(node):
    return {x.id for x in ast.walk(node)
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load)}

def scan_block(stmts, already, hits, fname):
    seen = set(already)
    for i, st in enumerate(stmts):
        if isinstance(st, ast.If):
            body_assigned = set()
            for b in st.body:
                body_assigned |= assigned_names(b)
            else_assigned = set()
            for b in st.orelse:
                else_assigned |= assigned_names(b)
            cond_only = body_assigned - else_assigned - seen
            if cond_only:
                for later in stmts[i + 1:]:
                    # a later sibling that LOADS a cond-only name without
                    # the same guard is the B2100 shape
                    used = loads_in(later) & cond_only
                    reassigned = assigned_names(later)
                    for u in sorted(used):
                        hits.append(f"{fname}:{later.lineno}: '{u}' assigned only in if-branch at line {st.lineno}, consumed later")
                    cond_only -= reassigned
                    if not cond_only:
                        break
        # nested blocks
        for attr in ("body", "orelse", "finalbody"):
            sub = getattr(st, attr, None)
            if sub and not isinstance(st, ast.If):
                scan_block(sub, seen | assigned_names(st) if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) else seen, hits, fname)
        seen |= assigned_names(st)

hits = []
roots = [Path("backtest"), Path("scripts")]
nfiles = 0
for root in roots:
    for p in sorted(root.rglob("*.py")):
        if "archive" in str(p) or "tests" in str(p):
            continue
        nfiles += 1
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as e:
            hits.append(f"{p}: SYNTAX ERROR {e}")
            continue
        # module level
        scan_block(tree.body, set(), hits, str(p))
        for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            args = {a.arg for a in fn.args.args + fn.args.kwonlyargs}
            scan_block(fn.body, args, hits, str(p))
print(f"scanned {nfiles} files; {len(hits)} candidates")
for h in hits[:60]:
    print(" ", h)
