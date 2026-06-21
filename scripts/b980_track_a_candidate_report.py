# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.15 P2 Track A consolidation per CHECKLIST #77.
"""B980 (2026-06-21): Phase P1 Bucket B B5 Track A candidate report.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.15 P2 Track A consolidation +
# Council 82 Option-g HYBRID verdict + owner directive 2026-06-21 'Approve
# your recommendations. Proceed. Council this.'

PURPOSE
-------
Enumerate Track A consolidation candidates using Council 82 HYBRID
methodology (signal-overlap + cluster-id AND-gate). Output owner-review
list for P2 reclassification phase.

Method:
  Axis 1 (structural): signal-overlap Jaccard from Section 1
    producer_index (>= 0.50 threshold per B709 phi precedent)
  Axis 2 (curated): B948 walk_verdict_ledger cluster_id (shared cluster
    = walk-doc-curated redundancy)
  Gate: AND of Axis 1 AND Axis 2 (conservative per project_no_apriori_
    strategy_pruning + B709 phi=0.297 false-positive precedent)

Output: output_audit/b980_track_a_candidate_report.json + summary.md

Per Council 82 fallback: if zero candidates surface, document terminal
finding (Option-f) + defer to post-R5 Sharpe-signature clustering.
"""
from __future__ import annotations

import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    from backtest.diagnostics.section_04_redundancy_phi_matrix import (
        _compute_pairwise_signal_overlap_jaccard,
        _load_cluster_id_map,
        SIGNAL_OVERLAP_TRACK_A_THRESHOLD,
    )
    from backtest.signals.screener import ALL_STRATEGIES

    sig_matrix = _compute_pairwise_signal_overlap_jaccard()
    cluster_map = _load_cluster_id_map()
    strategies = sorted(ALL_STRATEGIES.keys())

    # Build Track A candidate pairs (unordered; deduplicated)
    track_a_pairs: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for strat in strategies:
        self_cluster = cluster_map.get(strat)
        if not self_cluster:
            continue
        neighbors = sig_matrix.get(strat, {})
        for other, sig_jaccard in neighbors.items():
            if sig_jaccard < SIGNAL_OVERLAP_TRACK_A_THRESHOLD:
                continue
            if cluster_map.get(other) != self_cluster:
                continue
            pair = tuple(sorted([strat, other]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            track_a_pairs.append({
                "strategy_a": pair[0],
                "strategy_b": pair[1],
                "signal_overlap_jaccard": round(sig_jaccard, 4),
                "shared_cluster_id": self_cluster,
            })

    # Sort by jaccard desc
    track_a_pairs.sort(key=lambda x: -x["signal_overlap_jaccard"])

    # Cluster-level summary
    cluster_pair_counts = Counter(p["shared_cluster_id"] for p in track_a_pairs)
    strategies_in_candidates: set[str] = set()
    for p in track_a_pairs:
        strategies_in_candidates.add(p["strategy_a"])
        strategies_in_candidates.add(p["strategy_b"])

    n_strategies_with_cluster = sum(1 for c in cluster_map.values() if c)

    # Verdict per Council 82 fallback
    if len(track_a_pairs) == 0:
        verdict = "TERMINAL_HONEST_FINDING_PER_COUNCIL_82_FALLBACK"
        narrative = (
            "ZERO Track A consolidation candidates surface under hybrid "
            "(signal_overlap >= 0.50 AND shared cluster_id) gate. Per "
            "Council 82 fallback: escalate to Option-f terminal "
            "acknowledgment + defer consolidation to post-R5 Sharpe-"
            "signature clustering (Section 19 Axis 4 when R5 data lands)."
        )
    elif len(track_a_pairs) < 5:
        verdict = "SMALL_TRACK_A_CANDIDATE_SET"
        narrative = f"{len(track_a_pairs)} pairs surfaced; small set; owner reviews each manually."
    else:
        verdict = "NORMAL_TRACK_A_CANDIDATE_SET"
        narrative = f"{len(track_a_pairs)} pairs surfaced across {len(cluster_pair_counts)} clusters."

    out_path = REPO / "output_audit" / "b980_track_a_candidate_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "schema_version": "1.0",
            "batch": "B980",
            "council": "82_OPTION_G_HYBRID",
            "method": "hybrid_signal_overlap_plus_cluster_id_AND_gate",
            "signal_overlap_threshold": SIGNAL_OVERLAP_TRACK_A_THRESHOLD,
            "n_strategies_total": len(strategies),
            "n_strategies_with_cluster_id": n_strategies_with_cluster,
            "n_track_a_pairs": len(track_a_pairs),
            "n_strategies_in_track_a_pairs": len(strategies_in_candidates),
            "pairs_per_cluster": dict(cluster_pair_counts),
            "verdict": verdict,
            "narrative": narrative,
            "track_a_candidate_pairs": track_a_pairs,
        }, f, indent=2, default=str)

    logger.info("B980 Track A candidate report COMPLETE:")
    logger.info("  Strategies total: %d", len(strategies))
    logger.info("  Strategies with cluster_id (B948): %d", n_strategies_with_cluster)
    logger.info("  Track A candidate PAIRS: %d", len(track_a_pairs))
    logger.info("  Strategies in candidate pairs: %d", len(strategies_in_candidates))
    logger.info("  Verdict: %s", verdict)
    logger.info("  Narrative: %s", narrative)
    if track_a_pairs:
        logger.info("  Top-5 pairs by jaccard:")
        for p in track_a_pairs[:5]:
            logger.info("    %s ~ %s [%s] jaccard=%s",
                        p["strategy_a"], p["strategy_b"],
                        p["shared_cluster_id"], p["signal_overlap_jaccard"])
    logger.info("Output: %s", out_path.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
