#!/usr/bin/env python
"""Phase 1 quiet-fire investigation CSV (owner directive 2026-07-02).

Owner explicit scope (Council 234 clarification): include SILENT + STARVED +
MARGINAL strategies (0-99 fires) = 191 strategies from Batch A. Owner-driven
Phase 1 investigation of why these strategies aren't populating cells.

CSV columns:
  strategy_name       - registered name
  direction           - long / short / dual (inferred from name suffix)
  n_fires             - Batch A fires (unique trade entries)
  class               - SILENT (0) / STARVED (1-29) / MARGINAL (30-99)
  fired_regimes       - regimes where trades were observed
  regime_affinity     - registered STRATEGY_REGIME_AFFINITY (which regimes allowed)
  producer_signals    - key signals the strategy gates on (extracted from screener.py)
  disabled_flag       - listed in STRATEGIES_DISABLED_MISSING_PRODUCER?
  exploratory_flag    - grep screener.py for EXPLORATORY marker in docstring
  root_cause_hypothesis - my interpretation (needs owner review):
                        - PRODUCER_MISSING       (screener grep found no producer call)
                        - GATE_STACK_TOO_TIGHT   (>=4 gates + intersection near-empty)
                        - REGIME_AFFINITY_LIMITED (only crisis/bear + those absent)
                        - EXPLORATORY_INTENTIONAL (docstring says DO NOT DEPLOY)
                        - UNIVERSE_MISMATCH      (needs T3 or non-T1a; Batch A minimal)
                        - REVIEW_NEEDED          (couldn't auto-classify)

Usage:
  python scripts/build_quiet_fire_investigation_csv.py \
      --batch-dir output_batch_A_150 \
      --output output_batch_A_150/phase_1_quiet_fire_investigation.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# Ensure repo root is on path
_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


def infer_direction(name: str) -> str:
    if name.endswith("_short"):
        return "short"
    elif name.endswith("_long"):
        return "long"
    else:
        return "dual"


def extract_strategy_source(screener_source: str, strategy_name: str) -> str:
    """Extract the source code block for a strategy from screener.py.
    Strategies implement as `def strat_<name>(s, ...):` functions.
    Returns function body (from def to next top-level def) or empty if not found."""
    # Pattern: def strat_<name>(
    pattern = re.compile(rf'^def strat_{re.escape(strategy_name)}\s*\(', re.MULTILINE)
    match = pattern.search(screener_source)
    if not match:
        return ""
    # Find next top-level def or class
    start = match.start()
    next_def = re.search(r'^(def |class |# ---)', screener_source[start + 10:], re.MULTILINE)
    if next_def:
        end = start + 10 + next_def.start()
    else:
        end = min(len(screener_source), start + 4000)
    return screener_source[start:end]


def extract_gate_signals(strategy_block: str) -> list[str]:
    """Extract signals used in gate logic.
    First checks for explicit signals_used declaration; falls back to
    s.get(...) / signals.get(...) references in surrounding gate code."""
    if not strategy_block:
        return []
    signals = set()

    # Priority: explicit signals_used=[...] declaration in strategy dict
    su_match = re.search(r'["\']signals_used["\']\s*:\s*\[([^\]]+)\]', strategy_block)
    if su_match:
        for m in re.finditer(r'["\']([^"\']+)["\']', su_match.group(1)):
            signals.add(m.group(1))
        if signals:
            return sorted(signals)

    # Fallback: s.get("signal_name") or signals.get(...) references
    for pattern in [r's\.get\(\s*["\']([^"\']+)["\']',
                    r'signals\.get\(\s*["\']([^"\']+)["\']']:
        for m in re.finditer(pattern, strategy_block):
            signals.add(m.group(1))
    return sorted(signals)


def infer_root_cause(entry: dict, screener_source: str, regime_affinity: dict,
                    disabled_set: set, present_regimes: set) -> str:
    """Best-effort classification based on available evidence."""
    strat = entry["strategy_name"]

    # 1. Known disabled
    if strat in disabled_set:
        return "DISABLED_KNOWN"

    # 2. Look at strategy source block
    block = extract_strategy_source(screener_source, strat)

    # 3. EXPLORATORY marker
    if block and re.search(r"EXPLORATORY|DO NOT DEPLOY|exploratory", block, re.IGNORECASE):
        return "EXPLORATORY_INTENTIONAL"

    # 4. Producer missing
    if not block:
        return "REVIEW_NEEDED_STRATEGY_BLOCK_NOT_FOUND"

    # 5. Regime affinity limited
    affinity = regime_affinity.get(strat, [])
    if affinity and isinstance(affinity, (list, set, tuple)):
        allowed = set(affinity)
        if allowed and not (allowed & present_regimes):
            return f"REGIME_AFFINITY_LIMITED_to_{'|'.join(sorted(allowed))}"

    # 6. Universe mismatch heuristic
    if strat.startswith(("classification_change_",)):
        return "UNIVERSE_MISMATCH_CLASSIFICATION_CHANGE_NEEDS_T3"

    # 7. Gate stack too tight (>=4 gates + n_fires=0)
    signals = extract_gate_signals(block)
    if entry["n_fires"] == 0 and len(signals) >= 4:
        return f"GATE_STACK_TOO_TIGHT_{len(signals)}_signals"

    # 8. Default
    return "REVIEW_NEEDED"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    batch_dir = Path(args.batch_dir)
    trade_log = batch_dir / "trade_log.csv"
    if not trade_log.exists():
        print(f"ERROR: {trade_log} not found", file=sys.stderr)
        return 2

    # Load Batch A trade log
    df = pd.read_csv(trade_log)
    fires = df["strategy"].value_counts().to_dict()
    fired_regimes_by_strat = df.groupby("strategy")["regime"].agg(lambda s: sorted(set(s))).to_dict()

    # Load registered strategies
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.config import STRATEGIES_DISABLED_MISSING_PRODUCER
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY

    disabled_set = set()
    for s in STRATEGIES_DISABLED_MISSING_PRODUCER:
        name = s.name if hasattr(s, "name") else str(s)
        if name.startswith("strat_"):
            name = name[len("strat_"):]
        disabled_set.add(name)

    registered_names = []
    strategy_categories = {}
    for s in ALL_STRATEGIES:
        name = getattr(s, "name", None) or getattr(s, "__name__", None) or str(s)
        if name.startswith("strat_"):
            name = name[len("strat_"):]
        registered_names.append(name)
        strategy_categories[name] = getattr(s, "category", "unknown")

    # Load screener source
    screener_source = (Path("backtest") / "signals" / "screener.py").read_text(encoding="utf-8", errors="ignore")

    # Regimes present in trade log
    present_regimes = set(df["regime"].unique())

    # Build entries for all 191 strategies (SILENT + STARVED + MARGINAL)
    entries = []
    for strat in sorted(registered_names):
        n_fires = int(fires.get(strat, 0))
        if n_fires >= 100:
            continue  # VIABLE - skip
        if n_fires == 0:
            cls = "SILENT"
        elif n_fires < 30:
            cls = "STARVED"
        else:
            cls = "MARGINAL"

        entry = {
            "strategy_name": strat,
            "direction": infer_direction(strat),
            "category": strategy_categories.get(strat, "unknown"),
            "n_fires": n_fires,
            "class": cls,
            "fired_regimes": ",".join(fired_regimes_by_strat.get(strat, [])),
            "regime_affinity": ",".join(sorted(STRATEGY_REGIME_AFFINITY.get(strat, []))),
            "disabled_flag": strat in disabled_set,
            "exploratory_flag": False,  # populated below
            "producer_signals": "",
            "root_cause_hypothesis": "",
            "notes": "",
        }

        block = extract_strategy_source(screener_source, strat)
        signals = extract_gate_signals(block)
        entry["producer_signals"] = ",".join(signals[:12])  # cap at 12 for CSV readability
        if block and re.search(r"EXPLORATORY|DO NOT DEPLOY", block):
            entry["exploratory_flag"] = True

        entry["root_cause_hypothesis"] = infer_root_cause(
            entry, screener_source, STRATEGY_REGIME_AFFINITY, disabled_set, present_regimes
        )
        entries.append(entry)

    # Sort: SILENT first, then STARVED (by n_fires desc), then MARGINAL
    class_order = {"SILENT": 0, "STARVED": 1, "MARGINAL": 2}
    entries.sort(key=lambda e: (class_order[e["class"]], -e["n_fires"], e["strategy_name"]))

    # Write CSV
    out = Path(args.output)
    fieldnames = ["strategy_name", "direction", "category", "n_fires", "class",
                  "fired_regimes", "regime_affinity", "disabled_flag",
                  "exploratory_flag", "producer_signals", "root_cause_hypothesis", "notes"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for e in entries:
            w.writerow(e)

    # Summary
    print(f"Wrote {out}: {len(entries)} strategies")
    print()
    print("=== Class distribution ===")
    from collections import Counter
    class_counts = Counter(e["class"] for e in entries)
    for cls, c in class_counts.most_common():
        print(f"  {cls}: {c}")
    print()
    print("=== root_cause_hypothesis distribution ===")
    rc_counts = Counter(e["root_cause_hypothesis"] for e in entries)
    for rc, c in rc_counts.most_common():
        print(f"  {rc}: {c}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
