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


# B980 (2026-06-21) Council 82 Option-g HYBRID additions
# (signal-overlap + family-cluster AND-gate for Track A candidate).
SIGNAL_OVERLAP_TRACK_A_THRESHOLD = 0.50  # B709 phi=0.297 deemed NOT-redundant; 0.50 = honest middle


@lru_cache(maxsize=1)
def _load_strategy_signal_sets() -> dict[str, frozenset]:
    """Per-strategy signal-key set from B970+1 Section 1 producer_index.

    Reuses _parse_screener_for_strategy_signal_deps which parses
    screener.py AST and returns {strategy: [signal_keys]}.
    """
    try:
        from backtest.diagnostics.section_01_wiring_trace import (
            _parse_screener_for_strategy_signal_deps,
        )
    except Exception as e:
        logger.warning("Could not import Section 1 signal deps: %s", e)
        return {}
    deps = _parse_screener_for_strategy_signal_deps()
    return {strat: frozenset(sigs) for strat, sigs in deps.items()}


@lru_cache(maxsize=1)
def _compute_pairwise_signal_overlap_jaccard() -> dict[str, dict[str, float]]:
    """Compute pairwise signal-key Jaccard from Section 1 producer_index.

    Returns {strategy_a: {strategy_b: signal_jaccard, ...}}
    Memoized; symmetric matrix.
    """
    sig_sets = _load_strategy_signal_sets()
    strategies = sorted(sig_sets.keys())
    matrix: dict[str, dict[str, float]] = {s: {} for s in strategies}
    logger.info("Computing pairwise signal-overlap Jaccard for %d strategies (B980)...", len(strategies))
    for i, sa in enumerate(strategies):
        a = sig_sets[sa]
        if not a:
            continue
        for sb in strategies[i + 1:]:
            b = sig_sets[sb]
            if not b:
                continue
            j = _jaccard(a, b)
            if j > 0:
                matrix[sa][sb] = j
                matrix[sb][sa] = j
    logger.info("B980 signal-overlap matrix complete.")
    return matrix


@lru_cache(maxsize=1)
def _load_cluster_id_map() -> dict[str, str]:
    """Per-strategy cluster_id from B948 walk_verdict_ledger v2.

    Returns {strategy: cluster_id} (e.g., 'BR-1', 'CC-2', 'SM-3').
    Strategies not in ledger -> absent (no cluster).
    """
    ledger_path = REPO / "output_audit" / "walk_verdict_ledger_v2.json"
    if not ledger_path.exists():
        return {}
    try:
        data = json.load(open(ledger_path))
    except Exception:
        return {}
    ledger = data.get("ledger") or data.get("strategies") or {}
    result: dict[str, str] = {}
    for strat, entries in ledger.items():
        if not isinstance(entries, list) or not entries:
            continue
        cluster_id = entries[0].get("cluster_id")
        if cluster_id:
            result[strat] = cluster_id
    return result


def extract_section_04_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 4 redundancy data for a single strategy.

    B980 (2026-06-21) Council 82 Option-g HYBRID: combines two epistemic
    sources of redundancy:
      Axis 1 - structural: signal-overlap Jaccard from Section 1
        producer_index (>=0.50 threshold per B709 phi precedent)
      Axis 2 - curated: B948 walk_verdict_ledger cluster_id (shared
        cluster = walk-doc-curated redundancy)
      Axis 3 (B959): fire-bar Jaccard (preserved as supplementary;
        max_jaccard=0.0 across R4 cube proved degenerate at this scale)

    Track-A candidate gate (AND-gated for conservatism per
    project_no_apriori_strategy_pruning + B709 phi=0.297 false-positive
    precedent):
      signal_overlap_jaccard >= 0.50 AND shared cluster_id

    Strategies not in R4 (post-R4 additions) still get signal-overlap +
    cluster_id (Axis 1+2 available pre-R5); only Axis 3 fire-bar requires
    R4 cube data.
    """
    sets = _load_strategy_fire_sets()
    matrix = _compute_pairwise_jaccard_matrix()
    signal_matrix = _compute_pairwise_signal_overlap_jaccard()
    cluster_map = _load_cluster_id_map()
    fire_set = sets.get(strategy)
    in_r4_cube = fire_set is not None
    self_cluster = cluster_map.get(strategy)

    # Axis 1 - signal-overlap top-5
    signal_neighbors_raw = signal_matrix.get(strategy, {})
    signal_top_5 = sorted(signal_neighbors_raw.items(), key=lambda x: x[1], reverse=True)[:5]
    signal_top_5_list = [
        {
            "strategy": s,
            "signal_overlap_jaccard": round(j, 4),
            "shared_cluster_id": cluster_map.get(s) == self_cluster if self_cluster else False,
        }
        for s, j in signal_top_5
    ]

    # Axis 2 - shared cluster_id peers (excluding self)
    cluster_peers = [s for s, c in cluster_map.items() if c == self_cluster and s != strategy] if self_cluster else []

    # Hybrid Track-A candidates: AND-gate per Council 82
    hybrid_track_a_candidates = [
        s for s, j in signal_neighbors_raw.items()
        if j >= SIGNAL_OVERLAP_TRACK_A_THRESHOLD
        and self_cluster is not None
        and cluster_map.get(s) == self_cluster
    ]

    # Axis 3 - B959 fire-bar Jaccard (preserved as supplementary)
    fire_bar_top_5 = []
    fire_bar_max_jaccard = None
    fire_bar_max_neighbor = None
    if in_r4_cube:
        neighbors = matrix.get(strategy, {})
        sorted_neighbors = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:5]
        fire_bar_top_5 = [{"strategy": s, "fire_bar_jaccard": round(j, 4)} for s, j in sorted_neighbors]
        if sorted_neighbors:
            fire_bar_max_neighbor = sorted_neighbors[0][0]
            fire_bar_max_jaccard = round(sorted_neighbors[0][1], 4)

    if fire_set is None:
        # Post-R5 addition: Axis 1+2 still available; Axis 3 absent
        return {
            "n_fires_in_r4": 0,
            "in_r4_cube": False,
            "self_cluster_id": self_cluster,
            "n_cluster_peers": len(cluster_peers),
            "cluster_peers": cluster_peers[:10],
            "axis_1_signal_overlap_top_5": signal_top_5_list,
            "axis_2_shared_cluster_peers": cluster_peers[:10],
            "axis_3_fire_bar_top_5": [],
            "axis_3_max_jaccard_neighbor": None,
            "axis_3_max_jaccard_value": None,
            "hybrid_track_a_candidates": hybrid_track_a_candidates,
            "track_a_candidate": len(hybrid_track_a_candidates) > 0,
            "method": "hybrid_signal_overlap_plus_cluster_id_axis_3_unavailable_post_r5",
            "source": "Section 1 producer_index + B948 walk_verdict_ledger_v2 + R4 cube (Axis 3 unavailable for post-R5)",
            "threshold": SIGNAL_OVERLAP_TRACK_A_THRESHOLD,
            "memory_rule_reference": (
                "B980 Council 82 Option-g HYBRID: AND-gate signal_overlap_jaccard >= 0.50 "
                "AND shared cluster_id per project_no_apriori_strategy_pruning + B709 "
                "phi=0.297 false-positive precedent + DO-NOT-DELETE preservation."
            ),
        }
    return {
        "n_fires_in_r4": len(fire_set),
        "in_r4_cube": True,
        "self_cluster_id": self_cluster,
        "n_cluster_peers": len(cluster_peers),
        "cluster_peers": cluster_peers[:10],
        "axis_1_signal_overlap_top_5": signal_top_5_list,
        "axis_2_shared_cluster_peers": cluster_peers[:10],
        "axis_3_fire_bar_top_5": fire_bar_top_5,
        "axis_3_max_jaccard_neighbor": fire_bar_max_neighbor,
        "axis_3_max_jaccard_value": fire_bar_max_jaccard,
        "hybrid_track_a_candidates": hybrid_track_a_candidates,
        "track_a_candidate": len(hybrid_track_a_candidates) > 0,
        "method": "hybrid_signal_overlap_plus_cluster_id_with_fire_bar_supplementary",
        "source": "Section 1 producer_index + B948 walk_verdict_ledger_v2 + output_batch395_final/trade_exit_detail.csv",
        "threshold": SIGNAL_OVERLAP_TRACK_A_THRESHOLD,
        "memory_rule_reference": (
            "B980 Council 82 Option-g HYBRID (signal-overlap + cluster-id AND-gate); B959 fire-bar "
            "Jaccard preserved as Axis 3 supplementary (max_jaccard=0.0 across R4 = degenerate metric at "
            "this scale per B959 honest finding); per project_no_apriori_strategy_pruning + B709 "
            "phi=0.297 false-positive precedent + DO-NOT-DELETE preservation."
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
