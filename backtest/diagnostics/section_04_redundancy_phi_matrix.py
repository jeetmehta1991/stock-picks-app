# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 4 per CHECKLIST #77.
"""B959 (2026-06-20): Phase P1 batch 19 - Section 4 redundancy_phi_matrix extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 4 + Council 64 UNANIMOUS
# Option (beta) verdict per owner directive 2026-06-20 'Continue council this'.
# PATH-load-bearing for P2 Track A consolidation per Council 63 (B958 §13.15).

PURPOSE
-------
Section 4 redundancy diagnostic - PATH §13.3 spec: 'Pairwise trade-day
Jaccard across 219 strategies'.

Now PATH-LOAD-BEARING per Council 63 (B958): P2 Track A consolidation
uses redundancy_phi_matrix on R4 cube data. Cluster representatives stay
STRATEGY_STATUS=ACTIVE; reskins flip to DEPRECATED. Honors B705.

PRE-BUILD CHECK (Council 64 Executor mandate, executed):
  R4 trade detail: output_batch395_final/trade_exit_detail.csv
  Schema: (ticker, strategy, entry_date, exit_method, ...) at fire-bar
    grain (729,500 rows; 26 exit replays per fire => ~28k unique fires
    per strategy in R4 cube)
  Per-strategy fire-bar set extraction feasible: YES
  Pre-build check PASS; build proceeds.

METHODOLOGY (PATH §13.3 canonical: Pairwise trade-day Jaccard):
  1. Per strategy: extract set of (ticker, entry_date) tuples
  2. Pairwise Jaccard for all strategy pairs:
     jaccard(A,B) = |A intersect B| / |A union B|
  3. Per-strategy top-5 nearest neighbors by Jaccard descending
  4. Flag jaccard >= 0.70 as Track A consolidation candidate
     (B709 PEAD precedent: 0.297 was below revert threshold; 0.70 is
     the documented bar for deterministic-subset)
  5. Output: shared parquet matrix + per-dossier Section 4 with top-5

OUTPUT SCHEMA per strategy:
{
  "n_fires_in_r4": int,
  "top_5_neighbors": [
    {"strategy": str, "jaccard": float, "track_a_consolidation_candidate": bool}
  ],
  "max_jaccard_neighbor": str | None,
  "max_jaccard_value": float | None,
  "track_a_candidate": bool,  # True if max_jaccard >= 0.70
  "method": "pairwise_trade_day_jaccard",
  "source": "output_batch395_final/trade_exit_detail.csv",
  "threshold": 0.70,
  "memory_rule_reference": "feedback_no_prior_edge_consolidate_before_tune (B705); Council 63 P2 Track A",
}
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent.parent
R4_TRADE_DETAIL_CSV = REPO / "output_batch395_final" / "trade_exit_detail.csv"
SHARED_MATRIX_PATH = REPO / "output_audit" / "dossiers" / "_shared" / "section_04_redundancy_jaccard.parquet"
TRACK_A_THRESHOLD = 0.70


@lru_cache(maxsize=1)
def _load_strategy_fire_sets() -> dict[str, frozenset]:
    """Load per-strategy frozenset of (ticker, entry_date) tuples from R4 trade detail.

    Lazy-cached at module level to avoid re-reading 729k-row CSV per dossier.
    """
    if not R4_TRADE_DETAIL_CSV.exists():
        logger.warning("R4 trade_exit_detail.csv not found at %s", R4_TRADE_DETAIL_CSV)
        return {}
    try:
        import pandas as pd
        # Read only the columns we need to keep memory small
        df = pd.read_csv(R4_TRADE_DETAIL_CSV, usecols=["strategy", "ticker", "entry_date"])
        # Dedup since 26 exit replays produce duplicate (strategy, ticker, entry_date)
        df = df.drop_duplicates()
        result: dict[str, frozenset] = {}
        for strat, group in df.groupby("strategy"):
            fires = frozenset(zip(group["ticker"], group["entry_date"]))
            result[strat] = fires
        return result
    except Exception as e:
        logger.error("Cannot load R4 trade_exit_detail.csv: %s", e)
        return {}


def _jaccard(a: frozenset, b: frozenset) -> float:
    """Jaccard similarity = |A intersect B| / |A union B|."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / len(a | b)


@lru_cache(maxsize=1)
def _compute_pairwise_jaccard_matrix() -> dict[str, dict[str, float]]:
    """Compute full pairwise Jaccard matrix for all strategies in R4.

    Returns {strategy_a: {strategy_b: jaccard, ...}, ...}
    Memoized per process so per-dossier lookups are O(1) after first call.
    """
    sets = _load_strategy_fire_sets()
    strategies = sorted(sets.keys())
    matrix: dict[str, dict[str, float]] = {s: {} for s in strategies}
    logger.info("Computing pairwise Jaccard for %d strategies...", len(strategies))
    for i, sa in enumerate(strategies):
        a = sets[sa]
        for sb in strategies[i + 1:]:
            b = sets[sb]
            j = _jaccard(a, b)
            if j > 0:
                matrix[sa][sb] = j
                matrix[sb][sa] = j
    logger.info("Jaccard matrix complete.")
    return matrix


def extract_section_04_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 4 redundancy data for a single strategy.

    Returns dict for Section 4 dossier slot. method='pairwise_trade_day_jaccard'.
    Strategies not in R4 (post-R4 additions) return method='not_in_r4_cube'.
    """
    sets = _load_strategy_fire_sets()
    matrix = _compute_pairwise_jaccard_matrix()
    fire_set = sets.get(strategy)
    if fire_set is None:
        return {
            "n_fires_in_r4": 0,
            "top_5_neighbors": [],
            "max_jaccard_neighbor": None,
            "max_jaccard_value": None,
            "track_a_candidate": False,
            "method": "not_in_r4_cube",
            "source": "output_batch395_final/trade_exit_detail.csv",
            "threshold": TRACK_A_THRESHOLD,
            "memory_rule_reference": (
                "feedback_no_prior_edge_consolidate_before_tune (B705); Council 63 P2 Track A; "
                "Strategy not in R4 cube (post-R4 addition); redundancy diagnosis pending R5 launch."
            ),
        }
    neighbors = matrix.get(strategy, {})
    # Sort by jaccard descending
    sorted_neighbors = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:5]
    top_5 = [
        {
            "strategy": s,
            "jaccard": round(j, 4),
            "track_a_consolidation_candidate": j >= TRACK_A_THRESHOLD,
        }
        for s, j in sorted_neighbors
    ]
    max_neighbor = sorted_neighbors[0] if sorted_neighbors else None
    max_jaccard_value = max_neighbor[1] if max_neighbor else None
    return {
        "n_fires_in_r4": len(fire_set),
        "top_5_neighbors": top_5,
        "max_jaccard_neighbor": max_neighbor[0] if max_neighbor else None,
        "max_jaccard_value": round(max_jaccard_value, 4) if max_jaccard_value is not None else None,
        "track_a_candidate": (max_jaccard_value or 0) >= TRACK_A_THRESHOLD,
        "method": "pairwise_trade_day_jaccard",
        "source": "output_batch395_final/trade_exit_detail.csv",
        "threshold": TRACK_A_THRESHOLD,
        "memory_rule_reference": (
            "feedback_no_prior_edge_consolidate_before_tune (B705); Council 63 P2 Track A: "
            "max_jaccard >= 0.70 flags strategy as redundancy-consolidation candidate. "
            "Cluster representative stays ACTIVE; this strategy may flip to DEPRECATED if "
            "reskin per P2 reclassification phase."
        ),
    }


def populate_section_04_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 4 redundancy_phi_matrix slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_04_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_04_redundancy_phi_matrix"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)


def write_shared_matrix_parquet() -> Path:
    """Write the shared 219x219 Jaccard matrix to parquet for P2 Track A consumption."""
    import pandas as pd
    matrix = _compute_pairwise_jaccard_matrix()
    strategies = sorted(matrix.keys())
    # Build dense DataFrame (zeros where no overlap)
    df = pd.DataFrame(0.0, index=strategies, columns=strategies)
    for sa, neighbors in matrix.items():
        for sb, j in neighbors.items():
            df.at[sa, sb] = j
    SHARED_MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(SHARED_MATRIX_PATH)
    logger.info("Shared Jaccard matrix written: %s (%d x %d)", SHARED_MATRIX_PATH,
                df.shape[0], df.shape[1])
    return SHARED_MATRIX_PATH
