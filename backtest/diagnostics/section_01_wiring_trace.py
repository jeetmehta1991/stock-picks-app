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


@lru_cache(maxsize=1)
def _load_signal_producer_index() -> dict[str, str]:
    """Build static index: signal_key -> producer_module that emits it.

    Walks backtest/signals/*.py, backtest/data/signal_loader.py, scans for
    assignment patterns to signal dicts: s["key"] = ... or signals_out["key"] = ...
    Returns flat dict {signal_key: producer_filename}.
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
            for node in ast.walk(tree):
                # Pattern: s["key"] = ... or out["key"] = ...
                if isinstance(node, ast.Assign):
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Subscript) and isinstance(tgt.slice, ast.Constant):
                            if isinstance(tgt.slice.value, str):
                                index.setdefault(tgt.slice.value, py.name)
                # Pattern: dict literal { "key": value, ... }
                if isinstance(node, ast.Dict):
                    for k in node.keys:
                        if isinstance(k, ast.Constant) and isinstance(k.value, str):
                            index.setdefault(k.value, py.name)
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
