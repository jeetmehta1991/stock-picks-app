"""Batch 566 (2026-06-03) - Stage 4 step 1 of 4 per
PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md.

Reads per-strategy candidate JSONs + producer_zero audit + exit_method
analysis from an optimizer-output dir. Enumerates atomic proposed
changes by the 6 change classes defined in the workflow Stage 4 section.

Output: r4_proposed_changes.json - flat list of atomic rows that
becomes the input to step 2 (approvals.json init).

Each atomic row:
  {
    "candidate_id":    str,    # stable id: sha-derived from strat+class+detail
    "strategy":        str,
    "change_class":    int,    # 1..6 per workflow
    "change_class_name": str,
    "dimension_source":  str,  # dimension_a..i or producer_zero_audit or cube
    "change_detail":   str,    # the free-text proposal verbatim
    "structured":      dict,   # parsed structured fields (best-effort)
    "rationale_metrics": dict, # n_trades, sharpe, etc. so owner can size impact
    "config_touch_point": str  # which file would change at Stage 5
  }

Change classes (per workflow lines 326-336):
  1 STRATEGY_EXIT_OVERRIDE       -> backtest/config.py::STRATEGY_EXIT_OVERRIDE
  2 Entry-gate threshold loosen  -> backtest/signals/screener.py predicate
  3 Compound-logic restructure   -> backtest/signals/screener.py predicate
  4 Sizing tier remap            -> backtest/config.py sizing tier dict
  5 STRATEGY_REGIME_AFFINITY     -> backtest/config.py::STRATEGY_REGIME_AFFINITY
  6 Roster deprecation           -> backtest/config.py::DEPRECATED_STRATEGIES

Usage:
  python scripts/extract_proposed_changes.py \
    --input-dir C:/tmp/r4_optimization_candidates \
    --output    C:/tmp/r4_optimization_candidates/r4_proposed_changes.json
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import sys
from pathlib import Path


CLASS_NAMES = {
    1: "STRATEGY_EXIT_OVERRIDE",
    2: "ENTRY_GATE_LOOSEN",
    3: "COMPOUND_RESTRUCTURE",
    4: "SIZING_TIER_REMAP",
    5: "STRATEGY_REGIME_AFFINITY",
    6: "ROSTER_DEPRECATION",
}

CONFIG_TOUCH = {
    1: "backtest/config.py::STRATEGY_EXIT_OVERRIDE",
    2: "backtest/signals/screener.py::strat_<name> predicate",
    3: "backtest/signals/screener.py::strat_<name> compound restructure",
    4: "backtest/config.py sizing tier dict",
    5: "backtest/config.py::STRATEGY_REGIME_AFFINITY",
    6: "backtest/config.py::DEPRECATED_STRATEGIES",
}


def _id(strategy: str, change_class: int, change_detail: str) -> str:
    h = hashlib.sha1(
        f"{strategy}|{change_class}|{change_detail}".encode("utf-8")
    ).hexdigest()[:12]
    return f"r4-{h}"


def _parse_dim_d_exit(strategy: str, agg: dict, props: list, ranked: list) -> list:
    """Dim D proposals like 'best exit `X` has Sharpe N (n=M); 5-gate VERDICT'.

    Class 1 STRATEGY_EXIT_OVERRIDE. We extract the best exit + structured
    metrics so the owner can size impact.
    """
    rows = []
    for p in props:
        if not isinstance(p, str):
            continue
        m = re.search(
            r"best exit `([^`]+)` has Sharpe ([-\d.]+) \(n=(\d+)\); 5-gate (\w+)",
            p,
        )
        if not m:
            # Catch-all for non-matching free-text
            rows.append({
                "candidate_id": _id(strategy, 1, p),
                "strategy": strategy,
                "change_class": 1,
                "change_class_name": CLASS_NAMES[1],
                "dimension_source": "dimension_d_exit",
                "change_detail": p,
                "structured": {},
                "rationale_metrics": agg,
                "config_touch_point": CONFIG_TOUCH[1],
            })
            continue
        exit_name, sharpe, n, gate = m.group(1), float(m.group(2)), int(m.group(3)), m.group(4)
        rows.append({
            "candidate_id": _id(strategy, 1, p),
            "strategy": strategy,
            "change_class": 1,
            "change_class_name": CLASS_NAMES[1],
            "dimension_source": "dimension_d_exit",
            "change_detail": p,
            "structured": {
                "proposed_exit_method": exit_name,
                "cell_sharpe": sharpe,
                "cell_n": n,
                "five_gate_verdict": gate,
            },
            "rationale_metrics": agg,
            "config_touch_point": CONFIG_TOUCH[1],
        })
    return rows


def _parse_dim_b_compound(strategy: str, agg: dict, props: list) -> list:
    """Dim B free-text like 'clauses [...] fire 90%+ - removing wouldn\\'t reduce admission'.

    Maps to Class 3 COMPOUND_RESTRUCTURE (or Class 2 if clearly a loosening rec).
    The current optimizer emits mostly informational lines; we capture them
    so owner can decide which clauses to actually edit.
    """
    rows = []
    for p in props:
        if not isinstance(p, str):
            continue
        # Try to extract clause list
        m = re.search(r"clauses (\[[^\]]+\])", p)
        clauses = []
        if m:
            try:
                clauses = json.loads(m.group(1).replace("'", '"'))
            except Exception:
                pass
        change_class = 3  # default to compound restructure
        if "loosening" in p.lower() or "loosen" in p.lower():
            change_class = 2
        rows.append({
            "candidate_id": _id(strategy, change_class, p),
            "strategy": strategy,
            "change_class": change_class,
            "change_class_name": CLASS_NAMES[change_class],
            "dimension_source": "dimension_b_compound",
            "change_detail": p,
            "structured": {"clauses": clauses},
            "rationale_metrics": agg,
            "config_touch_point": CONFIG_TOUCH[change_class],
        })
    return rows


def _parse_dim_c_regime(strategy: str, agg: dict, props: list, per_regime: dict) -> list:
    """Dim C regime affinity. Class 5. AUTO-DEFERRED in Phase 1A-beta per
    workflow line 337 - status will be set to Deferred in step 2."""
    rows = []
    for p in props:
        if not isinstance(p, str):
            continue
        m = re.search(
            r"STRATEGY_REGIME_AFFINITY\[[^\]]+\] = \{([^}]+)\}",
            p,
        )
        regimes_pass = []
        if m:
            regimes_pass = [r.strip().strip("'\"") for r in m.group(1).split(",")]
        rows.append({
            "candidate_id": _id(strategy, 5, p),
            "strategy": strategy,
            "change_class": 5,
            "change_class_name": CLASS_NAMES[5],
            "dimension_source": "dimension_c_regime",
            "change_detail": p,
            "structured": {
                "pass_regimes": regimes_pass,
                "per_regime_verdicts": per_regime,
            },
            "rationale_metrics": agg,
            "config_touch_point": CONFIG_TOUCH[5],
        })
    return rows


def _parse_dim_e_sizing(strategy: str, agg: dict, e: dict) -> list:
    """Dim E tier_rec != current default (MEDIUM). Class 4."""
    tier = e.get("tier_rec", "")
    if not tier:
        return []
    # Treat MEDIUM as default; anything else is a remap candidate
    # Surface ALL non-MEDIUM recs - LOW (skip) is the most common (109/115)
    if tier.startswith("MEDIUM") and "HIGH" not in tier:
        return []
    detail = f"sizing tier_rec = {tier} (agg_sharpe {e.get('agg_sharpe')}, size_pct {e.get('size_pct')})"
    return [{
        "candidate_id": _id(strategy, 4, detail),
        "strategy": strategy,
        "change_class": 4,
        "change_class_name": CLASS_NAMES[4],
        "dimension_source": "dimension_e_sizing",
        "change_detail": detail,
        "structured": {
            "proposed_tier": tier,
            "size_pct": e.get("size_pct"),
            "agg_sharpe": e.get("agg_sharpe"),
        },
        "rationale_metrics": agg,
        "config_touch_point": CONFIG_TOUCH[4],
    }]


def _parse_dim_g_hold(strategy: str, agg: dict, props: list) -> list:
    """Dim G hold-duration proposals like 'consider time_stop_20d exit'.
    Class 1 STRATEGY_EXIT_OVERRIDE variant (time_stop family)."""
    rows = []
    for p in props:
        if not isinstance(p, str):
            continue
        m = re.search(r"time_stop_(\d+)d", p)
        days = int(m.group(1)) if m else None
        rows.append({
            "candidate_id": _id(strategy, 1, p),
            "strategy": strategy,
            "change_class": 1,
            "change_class_name": CLASS_NAMES[1],
            "dimension_source": "dimension_g_hold",
            "change_detail": p,
            "structured": {
                "proposed_exit_method": f"time_stop_{days}d" if days else None,
                "from_dimension": "hold-duration",
            },
            "rationale_metrics": agg,
            "config_touch_point": CONFIG_TOUCH[1],
        })
    return rows


def _derive_class6_deprecation(pz: dict) -> list:
    """Class 6 ROSTER_DEPRECATION (empirical-only per workflow line 335).

    The producer_zero audit's 'PRODUCER_LAYER_ZERO_LIKELY' bucket is the
    strict empirical-deprecation candidate set: zero fires + zero cells
    with n>=30 across all 26 exits.

    COMPOUND_RESTRICTIVE + SKIPPED_AT_ENGINE are NOT class-6 candidates -
    those have other change classes (2/3) as appropriate fix paths.
    """
    rows = []
    plzl = pz.get("buckets", {}).get("PRODUCER_LAYER_ZERO_LIKELY", [])
    for strat in plzl:
        detail = (
            f"DEPRECATED_STRATEGIES.add('{strat}') - "
            f"PRODUCER_LAYER_ZERO_LIKELY (0 fires across full R4 cube; "
            f"empirical gate per workflow line 335). Owner may instead "
            f"prefer per-strategy producer fix (e.g. SMC sparse-event B556 "
            f"or sector_history expansion B561)."
        )
        rows.append({
            "candidate_id": _id(strat, 6, detail),
            "strategy": strat,
            "change_class": 6,
            "change_class_name": CLASS_NAMES[6],
            "dimension_source": "producer_zero_audit",
            "change_detail": detail,
            "structured": {
                "bucket": "PRODUCER_LAYER_ZERO_LIKELY",
                "alternative_fixes": [
                    "investigate producer source data gap",
                    "investigate compound predicate restrictiveness",
                ],
            },
            "rationale_metrics": {"n_trades": 0, "fires": 0},
            "config_touch_point": CONFIG_TOUCH[6],
        })
    return rows


def extract_all(input_dir: Path) -> list:
    rows = []
    cand_files = [
        f for f in sorted(input_dir.glob("*.json"))
        if f.name not in {
            "producer_zero_post_cube_audit.json",
            "exit_method_analysis.json",
            "r4_proposed_changes.json",
            "approvals.json",
        }
    ]
    for f in cand_files:
        d = json.loads(f.read_text(encoding="utf-8"))
        strat = d.get("strategy", f.stem)
        agg = d.get("aggregate", {})
        b = d.get("dimension_b_compound", {})
        c = d.get("dimension_c_regime", {})
        dd = d.get("dimension_d_exit", {})
        e = d.get("dimension_e_sizing", {})
        g = d.get("dimension_g_hold", {})
        rows.extend(_parse_dim_d_exit(strat, agg, dd.get("proposals", []), dd.get("ranked", [])))
        rows.extend(_parse_dim_b_compound(strat, agg, b.get("proposals", [])))
        rows.extend(_parse_dim_c_regime(strat, agg, c.get("proposals", []), c.get("per_regime", {})))
        rows.extend(_parse_dim_e_sizing(strat, agg, e))
        rows.extend(_parse_dim_g_hold(strat, agg, g.get("proposals", [])))
    # Class 6 from producer_zero audit
    pz_path = input_dir / "producer_zero_post_cube_audit.json"
    if pz_path.exists():
        pz = json.loads(pz_path.read_text(encoding="utf-8"))
        rows.extend(_derive_class6_deprecation(pz))
    return rows


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    in_dir = Path(args.input_dir)
    out_path = Path(args.output)
    if not in_dir.exists():
        print(f"ERROR: input dir not found: {in_dir}", file=sys.stderr)
        return 1
    rows = extract_all(in_dir)
    # Summary per class
    by_class = {}
    for r in rows:
        by_class[r["change_class"]] = by_class.get(r["change_class"], 0) + 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Extracted {len(rows)} atomic proposed changes -> {out_path}")
    print("By change class:")
    for k in sorted(by_class.keys()):
        print(f"  Class {k} ({CLASS_NAMES[k]}): {by_class[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
