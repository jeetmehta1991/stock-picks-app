"""B951 (2026-06-20): Phase P1 batch 11 - Section 1 wiring trace coverage extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 1 + Council 55 UNANIMOUS
# 4/4 verdict per owner directive 2026-06-20 'Council this'.

PURPOSE
-------
For each strategy, extract per-strategy signal-dependency map:
  - signals_required: list of signal keys the strategy reads via s.get("KEY")
  - signals_wired: subset that have a producer module emitting that key
  - signals_orphan: required but no producer found (data wiring gap)
  - coverage_pct: 100 * wired / required (proxy for static wiring coverage)

DESIGN NOTE on 'NOT grep' description (Section 1 in PATH Section 13.3):
The PATH doc specifies coverage.py mode as preferred. coverage.py requires
actually running a canonical backtest under instrumentation, which is
expensive. This extractor ships STATIC AST analysis as a first-cut Section 1
column for the dossier. Static AST IS code-reading (not grep); coverage.py
upgrade can replace this without changing the schema. Honest first-cut per
Council 55 single-artifact mandate.

Output schema:
{
  "n_signals_required": int,
  "n_signals_wired": int,
  "n_signals_orphan": int,
  "wiring_coverage_pct": float,
  "signals_required": [],
  "signals_wired": [],
  "signals_orphan": [],
  "method": "static_ast" | "coverage_py",
  "limitation": str,
}
"""
from __future__ import annotations

import ast
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent.parent
SCREENER_PATH = REPO / "backtest" / "signals" / "screener.py"


def _expand_fstring_with_bindings(
    joined: ast.JoinedStr, bindings: dict[str, list[str]]
) -> list[str]:
    """Expand an f-string AST node into all literal strings given var bindings.

    bindings maps {var_name: [list of literal string values it takes]}.
    Returns expanded literals if every Name reference inside the f-string has
    a known binding; otherwise returns []. Conservative: only Name references
    (no attribute access, no method calls) are expanded.

    Example:
      f"above_avwap_{key}" with bindings={"key": ["20high", "20low"]}
      -> ["above_avwap_20high", "above_avwap_20low"]
    """
    # B985 (2026-06-21) Council 89 Option-5 honest-finding pivot
    # owner-approved per directive 'Approve your recommendation. Proceed
    # council this.' Walk-1 Sub-B SIGNAL_ORPHAN findings for 6 BB
    # strategies were 100% FALSE POSITIVE per source-verification of
    # technical.py::compute_bollinger lines 1280-1351. Pattern: loop
    # `for period, std_m in [(20,2.0),(20,1.5),(10,2.0)]:` followed by
    # `key = f"bb_{period}_{str(std_m).replace('.','')}"`. The previous
    # helper rejected `str(X).replace(A, B)` method-chain at the
    # FormattedValue level; extension handles this conservatively.
    #
    # Collect ordered list of segments: (kind, value_or_callable).
    segments: list[tuple[str, object]] = []
    for v in joined.values:
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            segments.append(("literal", v.value))
        elif isinstance(v, ast.FormattedValue):
            # (1) Simple Name reference
            if isinstance(v.value, ast.Name):
                varname = v.value.id
                if varname not in bindings:
                    return []
                segments.append(("var", varname))
            # (2) B985 EXTENSION: str(NAME).replace(LIT, LIT) chain
            #     Pattern: Call(Attribute(Call(Name('str'),[Name(X)]),'replace'),[Const(A),Const(B)])
            elif isinstance(v.value, ast.Call):
                resolved_transform = _try_resolve_str_method_chain(v.value, bindings)
                if resolved_transform is None:
                    return []
                segments.append(("xform", resolved_transform))
            else:
                return []
        else:
            return []
    # Cartesian-expand.
    results: list[str] = [""]
    for kind, val in segments:
        if kind == "literal":
            results = [r + val for r in results]
        elif kind == "var":
            results = [r + b for r in results for b in bindings[val]]
        elif kind == "xform":
            # val is a list of transformed strings (already expanded for the loop var)
            results = [r + b for r in results for b in val]
    return results


def _try_resolve_str_method_chain(
    call_node: ast.Call, bindings: dict[str, list[str]]
) -> list[str] | None:
    """Resolve a `str(X).replace(literal, literal)` chain over loop-var bindings.

    Pattern (and chained variants):
      ast.Call(
        func=ast.Attribute(
          value=ast.Call(func=ast.Name(id='str'), args=[ast.Name(id='X')]),
          attr='replace'),
        args=[ast.Constant(str), ast.Constant(str)])

    Returns list of resolved literal values (e.g. for std_m in [2.0, 1.5]:
    str(std_m).replace('.', '') -> ['20', '15']). Returns None on
    unrecognized pattern (caller must fall through to existing reject).
    """
    # Innermost: must be Call(Name('str'), [Name(X)])
    def _peel_str_call(node: ast.AST) -> str | None:
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "str":
            if len(node.args) == 1 and isinstance(node.args[0], ast.Name):
                return node.args[0].id
        return None

    # Iteratively peel .replace(A, B) / .lower() / .upper() etc.
    current = call_node
    transforms: list = []
    while isinstance(current, ast.Call) and isinstance(current.func, ast.Attribute):
        method = current.func.attr
        if method == "replace" and len(current.args) == 2:
            if not all(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in current.args):
                return None
            transforms.append(("replace", current.args[0].value, current.args[1].value))
        elif method in ("lower", "upper") and len(current.args) == 0:
            transforms.append((method,))
        else:
            return None
        current = current.func.value

    var_name = _peel_str_call(current)
    if var_name is None or var_name not in bindings:
        return None

    # Apply transforms in reverse (innermost-first)
    results = []
    for v in bindings[var_name]:
        s = str(v)
        for t in reversed(transforms):
            if t[0] == "replace":
                s = s.replace(t[1], t[2])
            elif t[0] == "lower":
                s = s.lower()
            elif t[0] == "upper":
                s = s.upper()
        results.append(s)
    return results


def _collect_intermediate_string_assigns(
    func_node: ast.FunctionDef, loop_bindings: dict[str, list[str]]
) -> dict[str, list[str]]:
    """Find intermediate var assignments like `key = f"macd_{fast}_{slow}_{sig}"`.

    For each `Assign` of a Name to either an `ast.Constant(str)` or `ast.JoinedStr`
    inside the function, attempt to expand it using the provided loop_bindings
    (plus any previously-resolved intermediate vars). Returns mapping of
    var_name -> list of possible string values. Intermediate vars are appended
    to the result so chained expansions resolve.

    Conservative: skips assignments where the RHS isn't a string constant or
    expandable f-string. Multiple assignments to the same name produce union.
    """
    resolved: dict[str, list[str]] = dict(loop_bindings)
    # Walk in source order so chained assignments resolve forward.
    for sub in ast.walk(func_node):
        if not isinstance(sub, ast.Assign):
            continue
        if len(sub.targets) != 1:
            continue
        tgt = sub.targets[0]
        if not isinstance(tgt, ast.Name):
            continue
        val_node = sub.value
        if isinstance(val_node, ast.Constant) and isinstance(val_node.value, str):
            resolved.setdefault(tgt.id, []).append(val_node.value)
        elif isinstance(val_node, ast.JoinedStr):
            expanded = _expand_fstring_with_bindings(val_node, resolved)
            for val in expanded:
                resolved.setdefault(tgt.id, []).append(val)
    return resolved


def _collect_loop_bindings(for_node: ast.For) -> dict[str, list[str]]:
    """Extract loop-variable -> list-of-literal-string-values mapping from a For node.

    Supports:
      for key in ["a", "b", "c"]:               -> {"key": ["a","b","c"]}
      for lookback, key in [(252,"a"),(50,"b")]: -> {"key": ["a","b"], "lookback": <numeric str>}
    Numeric values are stringified so multi-var f-strings like
      f"sma_{period}" with period=50 -> "sma_50" still resolve.
    Returns {} if the iterable isn't a literal list of constants/tuples.
    """
    bindings: dict[str, list[str]] = {}
    if not isinstance(for_node.iter, (ast.List, ast.Tuple)):
        return bindings
    items = for_node.iter.elts

    # Case A: single-variable loop  for X in [const, const, ...]
    if isinstance(for_node.target, ast.Name):
        vals: list[str] = []
        for el in items:
            if isinstance(el, ast.Constant):
                vals.append(str(el.value))
            else:
                return {}
        bindings[for_node.target.id] = vals
        return bindings

    # Case B: tuple unpacking  for (a, b) in [(c1,c2), ...]
    if isinstance(for_node.target, ast.Tuple):
        names = [t.id for t in for_node.target.elts if isinstance(t, ast.Name)]
        if len(names) != len(for_node.target.elts):
            return {}
        for name in names:
            bindings[name] = []
        for el in items:
            if not isinstance(el, ast.Tuple) or len(el.elts) != len(names):
                return {}
            for i, sub in enumerate(el.elts):
                if isinstance(sub, ast.Constant):
                    bindings[names[i]].append(str(sub.value))
                else:
                    return {}
        return bindings

    return {}


def _walk_with_for_context(node: ast.AST, for_stack: list[ast.For]):
    """Yield (sub_node, enclosing_for_stack) tuples via DFS."""
    yield node, list(for_stack)
    if isinstance(node, ast.For):
        for_stack = for_stack + [node]
    for child in ast.iter_child_nodes(node):
        yield from _walk_with_for_context(child, for_stack)


# B986 (2026-06-21) Council 90 Option-6 HYBRID owner-approved per
# directive 'Approve your recommendation. Proceed council this.':
# WIRED_VIA_CALL_GRAPH curated annotation set for signals wired via
# patterns Section 1 static AST audit doesn't trace (call-graph + dict-
# update + parquet-load + in-place assign in skipped screener.py).
#
# Same auditable-taxonomy pattern as MEASUREMENT_DISPUTED + STRATEGIES_
# DISABLED_MISSING_PRODUCER + EXPLORATORY_STRATEGIES per Contrarian
# lens (Council 90). Explicit, grep-able, test-pinnable.
#
# Each entry = signal_key -> (producer_module, evidence_anchor).
# Pre-flight verification REQUIRED before adding entries (smoke test on
# real ticker confirming signal fires).
WIRED_VIA_CALL_GRAPH = {
    # B986: sc_13d_filed_within_30d wired via compute_sec_edgar_signals
    # called from screener.py:8170-8176; smoke verified XRX/BEN/NEXT
    # 2026-06-21 (all fire True with documented SC 13D activist
    # filings). Producer at sec_edgar_extractor.py:206
    # (sc_13d_filed_within_days with lookback_days=30 kwarg via
    # compute_sec_edgar_signals line 327). Data path data_prefetch/
    # sec_edgar_decoded/SC_13D/*.parquet. Section 1 detection gap:
    # f-string emission uses function-parameter binding which AST
    # audit doesn't trace through cross-module call chain.
    "sc_13d_filed_within_30d": (
        "sec_edgar_extractor.py",
        "compute_sec_edgar_signals (B531 wire-in; screener.py:8170-8176)",
    ),
    # B986: cap_band wired via cap_band_from_market_cap at
    # screener.py:219; in-place assign at screener.py:7934
    # (signals["cap_band"] = cap_band_from_market_cap(info.get(
    # "market_cap"))). Strategy consumes at screener.py:6520
    # (strat_january_effect_long s.get("cap_band") check). Section 1
    # detection gap: producer lives IN screener.py which is explicitly
    # skipped (line 279) to avoid self-referencing audit cycles.
    "cap_band": (
        "screener.py",
        "cap_band_from_market_cap (BUG-290 Batch 314; screener.py:7934)",
    ),
}


@lru_cache(maxsize=1)
def _load_signal_producer_index() -> dict[str, str]:
    """Build static index: signal_key -> producer_module that emits it.

    Walks backtest/signals/*.py, backtest/data/signal_loader.py, scans for
    assignment patterns to signal dicts: s["key"] = ... or signals_out["key"] = ...
    Returns flat dict {signal_key: producer_filename}.

    B970+1 fix (Council 73 kappa-a): also expands f-string subscript assignments
    like `out[f"above_avwap_{key}"] = ...` by tracing the enclosing `for key in
    [literal,...]` loop. Pre-fix, ~60-70 valid signal keys (above_avwap_*,
    below_avwap_*, avwap_*_reclaim_*, sma_N, ema_N, etc.) were missing from
    the index, causing the SIGNAL_ORPHAN finding type to over-count by ~146
    rows in B956 triage queue.
    """
    index: dict[str, str] = {}
    signal_dirs = [
        REPO / "backtest" / "signals",
        REPO / "backtest" / "data",
    ]
    for d in signal_dirs:
        if not d.exists():
            continue
        for py in d.glob("*.py"):
            if py.name == "screener.py":
                continue
            try:
                tree = ast.parse(py.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue
            # First pass: simple Constant subscript assignments + Dict literals.
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Subscript) and isinstance(tgt.slice, ast.Constant):
                            if isinstance(tgt.slice.value, str):
                                index.setdefault(tgt.slice.value, py.name)
                if isinstance(node, ast.Dict):
                    for k in node.keys:
                        if isinstance(k, ast.Constant) and isinstance(k.value, str):
                            index.setdefault(k.value, py.name)
            # Second pass: f-string subscript assignments inside enclosing For
            # loops + intermediate-variable string assignments. The For-context
            # walker gives us enclosing For-loop bindings; the per-function
            # intermediate-var resolver handles patterns like
            #   key = f"macd_{fast}_{slow}_{sig}"
            #   result[f"{key}_bullish"] = ...
            # Pre-resolve intermediate var bindings per FunctionDef (cheap; one pass).
            func_intermediate_bindings: dict[int, dict[str, list[str]]] = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Gather all loop bindings from for-loops directly inside this function.
                    loop_bindings: dict[str, list[str]] = {}
                    for sub_for in ast.walk(node):
                        if isinstance(sub_for, ast.For):
                            for k, v in _collect_loop_bindings(sub_for).items():
                                # Append (not overwrite) so multiple loops contribute.
                                loop_bindings.setdefault(k, []).extend(v)
                    func_intermediate_bindings[id(node)] = (
                        _collect_intermediate_string_assigns(node, loop_bindings)
                    )

            # Map each AST node back to its enclosing FunctionDef for intermediate-var lookup.
            node_to_func: dict[int, ast.FunctionDef] = {}
            def _annotate(parent: ast.AST, current_func: ast.FunctionDef | None):
                for child in ast.iter_child_nodes(parent):
                    next_func = child if isinstance(child, ast.FunctionDef) else current_func
                    if next_func is not None:
                        node_to_func[id(child)] = next_func
                    _annotate(child, next_func)
            _annotate(tree, None)

            for sub_node, for_stack in _walk_with_for_context(tree, []):
                if not isinstance(sub_node, ast.Assign):
                    continue
                for tgt in sub_node.targets:
                    if not isinstance(tgt, ast.Subscript):
                        continue
                    if not isinstance(tgt.slice, ast.JoinedStr):
                        continue
                    # Merge bindings from all enclosing For loops (innermost wins on conflict).
                    bindings: dict[str, list[str]] = {}
                    for for_node in for_stack:
                        for k, v in _collect_loop_bindings(for_node).items():
                            bindings[k] = v
                    # Layer in intermediate-var bindings from enclosing function.
                    enclosing_func = node_to_func.get(id(sub_node))
                    if enclosing_func is not None:
                        for k, v in func_intermediate_bindings.get(
                            id(enclosing_func), {}
                        ).items():
                            if k not in bindings:
                                bindings[k] = v
                    expanded = _expand_fstring_with_bindings(tgt.slice, bindings)
                    for key in expanded:
                        index.setdefault(key, py.name)
    # B986 (2026-06-21) Council 90 Option-6: fold curated WIRED_VIA_
    # CALL_GRAPH entries into index. Each entry is explicitly auditable
    # per Contrarian lens; pre-flight smoke-verified before addition.
    for key, (producer_module, _evidence) in WIRED_VIA_CALL_GRAPH.items():
        index.setdefault(key, producer_module)
    return index


@lru_cache(maxsize=1)
def _parse_screener_for_strategy_signal_deps() -> dict[str, list[str]]:
    """Walk screener.py AST and extract per-strategy `s.get(\"KEY\")` and `s[\"KEY\"]` reads.

    Returns: {strategy_function_name: [signal_keys_referenced]}
    """
    deps: dict[str, list[str]] = {}
    try:
        tree = ast.parse(SCREENER_PATH.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        logger.error("Cannot parse screener.py: %s", e)
        return deps

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        # Strategy functions are named strat_<name>
        if not node.name.startswith("strat_"):
            continue
        strategy_key = node.name[len("strat_"):]
        signal_keys: list[str] = []
        # Walk function body for s.get("KEY") and s["KEY"] patterns
        for sub in ast.walk(node):
            # s.get("KEY", ...)
            if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)
                    and sub.func.attr == "get"
                    and isinstance(sub.func.value, ast.Name) and sub.func.value.id == "s"
                    and sub.args and isinstance(sub.args[0], ast.Constant)
                    and isinstance(sub.args[0].value, str)):
                signal_keys.append(sub.args[0].value)
            # s["KEY"]
            if (isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Name)
                    and sub.value.id == "s" and isinstance(sub.slice, ast.Constant)
                    and isinstance(sub.slice.value, str)):
                signal_keys.append(sub.slice.value)
        deps[strategy_key] = sorted(set(signal_keys))
    return deps


def extract_section_01_for_strategy(strategy: str) -> dict[str, Any]:
    """Static AST wiring trace for a single strategy.

    Returns dict for Section 1 dossier slot. Method='static_ast' (not coverage.py
    yet; first-cut per Council 55).
    """
    all_deps = _parse_screener_for_strategy_signal_deps()
    producer_index = _load_signal_producer_index()
    signals_required = all_deps.get(strategy, [])
    signals_wired = [k for k in signals_required if k in producer_index]
    signals_orphan = [k for k in signals_required if k not in producer_index]
    n_req = len(signals_required)
    n_wired = len(signals_wired)
    coverage = 100.0 * n_wired / n_req if n_req > 0 else None
    # Map wired signals to their producer module
    wiring_map = [
        {"signal": k, "producer": producer_index.get(k)} for k in signals_required
    ]
    return {
        "n_signals_required": n_req,
        "n_signals_wired": n_wired,
        "n_signals_orphan": len(signals_orphan),
        "wiring_coverage_pct": coverage,
        "signals_required": signals_required,
        "signals_wired": signals_wired,
        "signals_orphan": signals_orphan,
        "wiring_map": wiring_map,
        "method": "static_ast",
        "limitation": (
            "Static AST analysis. Does NOT trace runtime call path via "
            "coverage.py (preferred per PATH 13.3). Coverage.py upgrade is "
            "future B-N batch; current extractor sufficient for first-cut "
            "dossier column per Council 55."
        ),
    }
