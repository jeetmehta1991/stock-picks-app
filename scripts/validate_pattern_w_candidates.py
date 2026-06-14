"""scripts/validate_pattern_w_candidates.py

# Source: B755-COUNCIL chairman recommendation +
#   S4-B755-COUNCIL-PATTERN-W-DELETE-BUNDLE-A-8-A-19-A-21
# per CHECKLIST #77 + #106 (data-consumption audit).

Validates B755-COUNCIL Pattern W deletion candidates against the empirical
fire-bar matrix produced by `scripts/build_fire_bar_matrix.py`.

PURPOSE.
The council surfaced 3 DELETE candidates based on gate-text comparison:
- A-8  stochrsi_overbought_short    vs A-7 SHORT branch (minus regime gate)
- A-19 camarilla_rsi_obv_short      vs A-18 SHORT branch (IDENTICAL gates)
- A-21 cpr_narrow_momentum_short    vs A-20 SHORT branch (minus regime gate)

These verdicts were gate-text comparisons -- NOT empirical fire-bar overlap
measurements. Per advisor C (Contrarian): "A-19 IDENTICAL -- sure or
silently-no-op gate? OBV has B748c-class temporal-coverage holes. Two
strategies firing on the same gates because one of the gates is silently
no-op is a BUG not a duplicate."

This script consumes the fire-bar similarity output (Jaccard + phi
correlation per (strategy_a, strategy_b, direction) pair) and:

(1) **Validates council's 3 named candidates**: confirms Jaccard >= 0.85
    AND phi-correlation >= 0.70 (or surfaces lower-than-expected overlap
    indicating gate-text comparison was wrong).

(2) **Surfaces additional Pattern W candidates** the council missed via
    eyeball: any (strategy_a, strategy_b) pair with Jaccard >= 0.85
    becomes a DELETE candidate regardless of gate-text similarity.

(3) **Reports Pattern J consolidation candidates** (phi >= 0.70):
    pre-cube routing candidates per B709 PEAD-restore phi threshold.

OUTPUT.
JSON report at output_audit/pattern_w_validation_<tag>.json:
{
  "meta": {input matrix path, n_pairs_audited, ...},
  "council_named_candidates": [
    {
      "candidate": "A-19 (camarilla_rsi_obv_short)",
      "vs": "A-18 (camarilla_rsi_obv) SHORT branch",
      "council_verdict": "HIGHEST_CONFIDENCE_DELETE",
      "empirical_jaccard": float,
      "empirical_phi": float,
      "n_a": int, "n_b": int, "n_both": int,
      "empirical_verdict":
        "CONFIRMED" (jaccard >= 0.85) /
        "MARGINAL" (0.50 <= jaccard < 0.85) /
        "REJECTED" (jaccard < 0.50 -- gate-text comparison wrong) /
        "INSUFFICIENT_DATA" (n_a or n_b < 30)
    },
    ...
  ],
  "additional_pattern_w_candidates": [
    {"strategy_a", "strategy_b", "direction", "jaccard", "phi",
     "verdict": "DELETE_CANDIDATE_NEW"},
    ...
  ],
  "pattern_j_candidates": [
    {"strategy_a", "strategy_b", "direction", "phi", "jaccard",
     "verdict": "CONSOLIDATION_CANDIDATE"},
    ...
  ]
}

USAGE.
  # Validate against smoke output (will likely have 0 pairs):
  python scripts/validate_pattern_w_candidates.py \
      --similarity output_audit/fire_bar_similarity_cluster_a_smoke.parquet

  # Validate against demo output (real Pattern W findings expected):
  python scripts/validate_pattern_w_candidates.py \
      --similarity output_audit/fire_bar_similarity_cluster_a_demo.parquet

  # Validate against full output:
  python scripts/validate_pattern_w_candidates.py --full
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

logger = logging.getLogger("validate_pattern_w_candidates")

REPO_ROOT = Path(_REPO)
OUTPUT_DIR = REPO_ROOT / "output_audit"

# Thresholds per council chairman + B709 PEAD-restore precedent.
JACCARD_THRESHOLD_DELETE = 0.85
JACCARD_THRESHOLD_MARGINAL = 0.50
PHI_THRESHOLD_CONSOLIDATION = 0.70
MIN_N_FOR_VALIDATION = 30

# Council's 3 named DELETE candidates per B755-COUNCIL TIER 3.7 ticket.
# Each entry: (candidate_short_name, vs_short_name, direction, council_verdict_note)
COUNCIL_DELETE_CANDIDATES: list[dict] = [
    {
        "candidate_strategy": "stochrsi_overbought_short",
        "vs_strategy": "stochrsi_oversold",
        "direction": "short",
        "council_verdict": "DELETE_CANDIDATE",
        "council_basis": "A-8 vs A-7 SHORT branch: A-8 lacks below_ema_200 regime gate; otherwise identical",
    },
    {
        "candidate_strategy": "camarilla_rsi_obv_short",
        "vs_strategy": "camarilla_rsi_obv",
        "direction": "short",
        "council_verdict": "HIGHEST_CONFIDENCE_DELETE",
        "council_basis": "A-19 vs A-18 SHORT branch: gates IDENTICAL post-B628 F1 + B629 F1 silent-gap closure",
    },
    {
        "candidate_strategy": "cpr_narrow_momentum_short",
        "vs_strategy": "cpr_narrow_momentum",
        "direction": "short",
        "council_verdict": "DELETE_CANDIDATE",
        "council_basis": "A-21 vs A-20 SHORT branch: A-21 lacks below_ema_200 regime gate",
    },
]


def _classify_pair_verdict(jaccard: float, phi: float,
                            n_a: int, n_b: int) -> str:
    """Per-pair verdict per chairman thresholds."""
    if n_a < MIN_N_FOR_VALIDATION or n_b < MIN_N_FOR_VALIDATION:
        return "INSUFFICIENT_DATA"
    if jaccard >= JACCARD_THRESHOLD_DELETE:
        return "CONFIRMED"
    if jaccard >= JACCARD_THRESHOLD_MARGINAL:
        return "MARGINAL"
    return "REJECTED"


def _lookup_pair(
    similarity_df: pd.DataFrame,
    strategy_a: str,
    strategy_b: str,
    direction: str,
) -> Optional[dict]:
    """Find a specific (strategy_a, strategy_b, direction) pair in the
    similarity DataFrame. compute_pairwise_similarity emits each pair
    once with alphabetical ordering on (strategy_a, strategy_b).
    """
    # Normalize alphabetical ordering
    s1, s2 = sorted([strategy_a, strategy_b])
    mask = (
        (similarity_df["strategy_a"] == s1)
        & (similarity_df["strategy_b"] == s2)
        & (similarity_df["direction"] == direction)
    )
    matches = similarity_df[mask]
    if matches.empty:
        return None
    row = matches.iloc[0]
    return {
        "strategy_a": row["strategy_a"],
        "strategy_b": row["strategy_b"],
        "direction": row["direction"],
        "n_a": int(row["n_a"]),
        "n_b": int(row["n_b"]),
        "n_both": int(row["n_both"]),
        "jaccard": float(row["jaccard"]),
        "phi": float(row["phi_correlation"]),
    }


def validate_council_candidates(
    similarity_df: pd.DataFrame,
) -> list[dict]:
    """For each of the 3 council Pattern W candidates, look up the
    empirical similarity and assign a verdict.
    """
    results = []
    for cand in COUNCIL_DELETE_CANDIDATES:
        lookup = _lookup_pair(
            similarity_df,
            cand["candidate_strategy"],
            cand["vs_strategy"],
            cand["direction"],
        )
        if lookup is None:
            results.append({
                **cand,
                "empirical_verdict": "NOT_FOUND_IN_SIMILARITY_MATRIX",
                "empirical_jaccard": None,
                "empirical_phi": None,
                "n_a": 0,
                "n_b": 0,
                "n_both": 0,
                "note": "Pair absent; possible no fires for either strategy in the run window",
            })
            continue
        verdict = _classify_pair_verdict(
            lookup["jaccard"], lookup["phi"],
            lookup["n_a"], lookup["n_b"],
        )
        results.append({
            **cand,
            "empirical_jaccard": lookup["jaccard"],
            "empirical_phi": lookup["phi"],
            "n_a": lookup["n_a"],
            "n_b": lookup["n_b"],
            "n_both": lookup["n_both"],
            "empirical_verdict": verdict,
            "agreement_with_council": (
                "AGREES" if verdict == "CONFIRMED"
                else "DISAGREES" if verdict == "REJECTED"
                else "PARTIAL" if verdict == "MARGINAL"
                else "PENDING"
            ),
        })
    return results


def surface_additional_pattern_w(
    similarity_df: pd.DataFrame,
    council_names: set[tuple[str, str, str]],
) -> list[dict]:
    """Find Jaccard >= 0.85 pairs the council DIDN'T name as candidates."""
    if similarity_df.empty:
        return []
    qualified = similarity_df[
        (similarity_df["jaccard"] >= JACCARD_THRESHOLD_DELETE)
        & (similarity_df["n_a"] >= MIN_N_FOR_VALIDATION)
        & (similarity_df["n_b"] >= MIN_N_FOR_VALIDATION)
    ]
    results = []
    for _, row in qualified.iterrows():
        pair_key = tuple(sorted([row["strategy_a"], row["strategy_b"]])) + (row["direction"],)
        if pair_key in council_names:
            continue
        results.append({
            "strategy_a": row["strategy_a"],
            "strategy_b": row["strategy_b"],
            "direction": row["direction"],
            "jaccard": float(row["jaccard"]),
            "phi": float(row["phi_correlation"]),
            "n_a": int(row["n_a"]),
            "n_b": int(row["n_b"]),
            "n_both": int(row["n_both"]),
            "verdict": "DELETE_CANDIDATE_NEW",
            "basis": "Jaccard >= 0.85 fire-bar overlap; council did not surface this pair",
        })
    return results


def surface_pattern_j_candidates(
    similarity_df: pd.DataFrame,
) -> list[dict]:
    """Pattern J consolidation candidates per phi-correlation >= 0.70."""
    if similarity_df.empty:
        return []
    qualified = similarity_df[
        (similarity_df["phi_correlation"] >= PHI_THRESHOLD_CONSOLIDATION)
        & (similarity_df["n_a"] >= MIN_N_FOR_VALIDATION)
        & (similarity_df["n_b"] >= MIN_N_FOR_VALIDATION)
    ]
    results = []
    for _, row in qualified.iterrows():
        results.append({
            "strategy_a": row["strategy_a"],
            "strategy_b": row["strategy_b"],
            "direction": row["direction"],
            "phi": float(row["phi_correlation"]),
            "jaccard": float(row["jaccard"]),
            "n_a": int(row["n_a"]),
            "n_b": int(row["n_b"]),
            "n_both": int(row["n_both"]),
            "verdict": "CONSOLIDATION_CANDIDATE",
            "basis": (
                f"phi-correlation >= {PHI_THRESHOLD_CONSOLIDATION} per B709 "
                f"PEAD-restore threshold"
            ),
        })
    return sorted(results, key=lambda r: -r["phi"])


def run_validation(similarity_path: Path) -> dict:
    """Main entry."""
    if not similarity_path.exists():
        return {
            "meta": {
                "as_of_run": datetime.now().isoformat(),
                "similarity_input": str(similarity_path),
                "error": "input similarity matrix Parquet not found",
            },
            "council_named_candidates": [],
            "additional_pattern_w_candidates": [],
            "pattern_j_candidates": [],
        }

    df = pd.read_parquet(similarity_path)
    logger.info("Loaded similarity matrix: %d pairs", len(df))

    council_results = validate_council_candidates(df)
    council_keys = {
        tuple(sorted([r["candidate_strategy"], r["vs_strategy"]])) + (r["direction"],)
        for r in council_results
    }
    additional = surface_additional_pattern_w(df, council_keys)
    pattern_j = surface_pattern_j_candidates(df)

    return {
        "meta": {
            "as_of_run": datetime.now().isoformat(),
            "similarity_input": str(similarity_path),
            "n_pairs_audited": len(df),
            "thresholds": {
                "jaccard_delete": JACCARD_THRESHOLD_DELETE,
                "jaccard_marginal": JACCARD_THRESHOLD_MARGINAL,
                "phi_consolidation": PHI_THRESHOLD_CONSOLIDATION,
                "min_n_for_validation": MIN_N_FOR_VALIDATION,
            },
        },
        "council_named_candidates": council_results,
        "additional_pattern_w_candidates": additional,
        "pattern_j_candidates": pattern_j,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Validate Pattern W candidates per "
                    "S4-B755-COUNCIL-PATTERN-W-DELETE-BUNDLE.",
    )
    p.add_argument("--similarity", default=None,
                   help="Path to fire_bar_similarity_*.parquet (default smoke output)")
    p.add_argument("--output", default=None,
                   help="Output JSON path (default output_audit/...)")
    p.add_argument("--smoke", action="store_true",
                   help="Use smoke similarity matrix as input")
    p.add_argument("--demo", action="store_true",
                   help="Use demo similarity matrix as input")
    p.add_argument("--full", action="store_true",
                   help="Use full similarity matrix as input")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    args = _build_arg_parser().parse_args(argv)

    if args.smoke:
        sim_path = OUTPUT_DIR / "fire_bar_similarity_cluster_a_smoke.parquet"
        tag = "smoke"
    elif args.demo:
        sim_path = OUTPUT_DIR / "fire_bar_similarity_cluster_a_demo.parquet"
        tag = "demo"
    elif args.full:
        sim_path = OUTPUT_DIR / "fire_bar_similarity_cluster_a_full.parquet"
        tag = "full"
    elif args.similarity:
        sim_path = Path(args.similarity)
        tag = sim_path.stem
    else:
        # Default: smoke
        sim_path = OUTPUT_DIR / "fire_bar_similarity_cluster_a_smoke.parquet"
        tag = "smoke"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.output) if args.output else (
        OUTPUT_DIR / f"pattern_w_validation_{tag}.json"
    )

    logger.info("Validating against %s", sim_path)
    report = run_validation(sim_path)
    out_path.write_text(json.dumps(report, indent=2, default=str))

    # Stdout summary
    meta = report["meta"]
    print(f"\n=== Pattern W validation {tag} complete ===")
    print(f"Similarity input       : {sim_path}")
    print(f"Pairs audited          : {meta.get('n_pairs_audited', 0)}")
    print(f"\nCouncil named candidates ({len(report['council_named_candidates'])}):")
    for c in report["council_named_candidates"]:
        print(f"  {c['candidate_strategy']:35s} vs {c['vs_strategy']:30s} | "
              f"{c['direction']:5s} | "
              f"verdict={c['empirical_verdict']:25s} | "
              f"council={c['council_verdict']}")
    print(f"\nAdditional Pattern W candidates ({len(report['additional_pattern_w_candidates'])}):")
    for c in report["additional_pattern_w_candidates"][:10]:
        print(f"  {c['strategy_a']:30s} vs {c['strategy_b']:30s} | "
              f"{c['direction']:5s} | jaccard={c['jaccard']:.3f}")
    print(f"\nPattern J consolidation candidates ({len(report['pattern_j_candidates'])}):")
    for c in report["pattern_j_candidates"][:10]:
        print(f"  {c['strategy_a']:30s} vs {c['strategy_b']:30s} | "
              f"{c['direction']:5s} | phi={c['phi']:.3f}")
    print(f"\nOutput                 : {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
