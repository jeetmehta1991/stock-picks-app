"""Batch 621 (2026-06-08) -- fire-count audit across ALL registered
strategies per CHECKLIST #105 (k) tooling.

Runs the B619 fire-count estimator on every strategy in ALL_STRATEGIES.
For each strategy: extracts gate list from `s.get("...")` calls in the
function body via inspect.getsource(), passes to estimate(), tabulates
verdicts.

Output:
  - Sorted table (lowest fires/yr first) - FAIL/WARN candidates surface
    at the top
  - Per-verdict counts (PASS_CUBE / WARN / FAIL / INCOMPLETE_PRIORS)
  - JSON file `output_audit/fire_count_audit.json` for downstream use

Caveat: gate extraction is regex-based on `s.get("name", ...)` calls.
Strategies that use composite helpers (e.g. _has_smart_money_buy) or
threshold comparisons on numeric signals are captured but may need
manual review. INCOMPLETE_PRIORS verdicts flag those for follow-up.

USAGE:
  python scripts/audit_fire_counts.py [--threshold 30] [--json]
"""
from __future__ import annotations

import argparse
import inspect
import json
import re
import sys
from pathlib import Path

# Make scripts/ importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.estimate_fire_count import estimate, PRIOR_RATES


GATE_RE = re.compile(r's\.get\(\s*"([a-zA-Z_][a-zA-Z0-9_]*)"')
# Detect OR composites where multiple gates can satisfy one logical
# condition (the regex AND-extraction over-restricts these).
OR_GATE_RE = re.compile(r'\bor\s+s\.get|or\s*\(\s*s\.get|or\s*\(\s*\(.*s\.get')
# Detect helper functions like _has_smart_money_buy which encode OR
# composites internally.
HELPER_RE = re.compile(r'_has_smart_money_(?:buy|sell)\s*\(')


def extract_gates(strategy_fn) -> list[str]:
    """Extract gate signal names from a strategy function via regex on
    s.get("name", ...) calls. Returns unique names in order of first
    appearance."""
    try:
        src = inspect.getsource(strategy_fn)
    except (TypeError, OSError):
        return []
    seen = set()
    gates = []
    for m in GATE_RE.finditer(src):
        name = m.group(1)
        if name not in seen:
            seen.add(name)
            gates.append(name)
    return gates


def has_or_composite(strategy_fn) -> bool:
    """Detect whether a strategy contains OR composites (logical OR
    between gates) or composite helper calls. The audit's INDEPENDENCE-
    PRODUCT-AND estimator over-restricts strategies with OR clauses,
    producing FALSE FAIL_FIRE_STARVED verdicts on those. This flag
    lets the audit caller filter or annotate accordingly."""
    try:
        src = inspect.getsource(strategy_fn)
    except (TypeError, OSError):
        return False
    return bool(OR_GATE_RE.search(src)) or bool(HELPER_RE.search(src))


def audit_all() -> dict:
    """Run estimator on every registered strategy. Returns dict with
    per-strategy results + summary counts."""
    from backtest.signals.screener import ALL_STRATEGIES
    results = []
    for name, fn in ALL_STRATEGIES.items():
        gates = extract_gates(fn)
        or_flag = has_or_composite(fn)
        if not gates and not or_flag:
            results.append({
                "strategy": name,
                "gates": [],
                "has_or_composite": False,
                "fires_per_year_upper_bound": None,
                "verdict": "NO_GATES_EXTRACTED",
                "missing_priors": [],
            })
            continue
        r = estimate(gates=gates) if gates else {
            "fires_per_year_upper_bound": None,
            "verdict": "NO_GATES_EXTRACTED",
            "missing_priors": [],
        }
        # If verdict is FAIL_FIRE_STARVED but strategy has OR composite,
        # flag as FAIL_BUT_HAS_OR (likely false-positive; manual review
        # required). Same for WARN.
        verdict = r["verdict"]
        if or_flag and verdict in ("FAIL_FIRE_STARVED", "WARN_FIRE_STARVED"):
            verdict = f"{verdict}_BUT_HAS_OR"
        results.append({
            "strategy": name,
            "gates": gates,
            "has_or_composite": or_flag,
            "fires_per_year_upper_bound": r["fires_per_year_upper_bound"],
            "verdict": verdict,
            "missing_priors": r["missing_priors"],
        })

    # Summary by verdict
    counts = {}
    for r in results:
        v = r["verdict"]
        counts[v] = counts.get(v, 0) + 1

    return {
        "total_strategies": len(results),
        "verdict_counts": counts,
        "results": results,
    }


def _format_table(audit: dict, threshold: float | None = None) -> str:
    """Format audit results as a sorted table. If threshold given, only
    show strategies with fires/yr <= threshold (or no estimate)."""
    rows = audit["results"]
    # Sort: missing first (highest priority for follow-up), then by
    # fires/yr ascending (FAIL at top).
    def sort_key(r):
        v = r["verdict"]
        f = r["fires_per_year_upper_bound"]
        # FAIL_FIRE_STARVED first, then WARN, then INCOMPLETE, then PASS
        order = {
            "FAIL_FIRE_STARVED": 0,
            "WARN_FIRE_STARVED": 1,
            "INCOMPLETE_PRIORS": 2,
            "NO_GATES_EXTRACTED": 3,
            "PASS_CUBE": 4,
        }
        return (order.get(v, 9), f if f is not None else float("inf"))
    rows = sorted(rows, key=sort_key)

    lines = []
    lines.append("=" * 100)
    lines.append("FIRE-COUNT AUDIT -- CHECKLIST #105 (k) sweep across ALL_STRATEGIES")
    lines.append("=" * 100)
    lines.append(f"Total strategies audited: {audit['total_strategies']}")
    lines.append(f"Verdict distribution:")
    for v, c in sorted(audit["verdict_counts"].items()):
        lines.append(f"  {v}: {c}")
    lines.append("")
    lines.append(f"{'Strategy':<55} {'Fires/yr (UB)':>14} {'Gates':>6} {'Verdict'}")
    lines.append("-" * 100)
    for r in rows:
        if threshold is not None and r["verdict"] not in (
            "FAIL_FIRE_STARVED", "WARN_FIRE_STARVED",
            "INCOMPLETE_PRIORS", "NO_GATES_EXTRACTED",
        ):
            if r["fires_per_year_upper_bound"] is not None and \
               r["fires_per_year_upper_bound"] > threshold:
                continue
        f = r["fires_per_year_upper_bound"]
        f_str = f"{f:>14.2f}" if f is not None else f"{'(n/a)':>14}"
        lines.append(f"{r['strategy']:<55} {f_str} {len(r['gates']):>6} {r['verdict']}")
    lines.append("=" * 100)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--threshold", type=float, default=None,
        help="Only show strategies with fires/yr <= threshold (and "
             "all FAIL/WARN/INCOMPLETE). Default: show all.")
    parser.add_argument(
        "--json", action="store_true",
        help="Output JSON to stdout")
    parser.add_argument(
        "--save-json", action="store_true",
        help="Save full results to output_audit/fire_count_audit.json")
    args = parser.parse_args()

    audit = audit_all()

    if args.save_json:
        out_path = Path("output_audit/fire_count_audit.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(audit, indent=2, default=str), encoding="utf-8")
        print(f"Saved: {out_path}")

    if args.json:
        print(json.dumps(audit, indent=2, default=str))
    else:
        print(_format_table(audit, threshold=args.threshold))


if __name__ == "__main__":
    main()
