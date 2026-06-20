# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 19 per CHECKLIST #77.
"""B960 (2026-06-20): Phase P1 batch 20 - Section 19 closest_neighbor_cluster extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 19 + Council 65 UNANIMOUS
# 4/4 verdict per owner directive 2026-06-20 'Council this. Approve your rec. Continue.'

PURPOSE
-------
Section 19 = PATH-load-bearing for P4 stratification per §13.5:
  P4 'Per-strategy walks (sampled; 30 stratified by cluster)'.
  Stratification requires every strategy to carry a cluster_id signature.

PATH §13.3 row 19 spec (canonical):
  'Closest-passing-neighbor + family + cluster_id'
  'Hierarchical clustering on sharpe-signature + signal-overlap + regime-bias'

PRE-BUILD CHECK (Council 65 Executor mandate, executed before coding):
  ALL_STRATEGIES roster: 219 strategies (post-B874 deletion)         OK
  Section 1 signals_required (B951): per-strategy signal lists       OK
  Section 5 regime_affinity (B953): per-strategy regime set          OK
  Section 4 Jaccard matrix (B959): per-strategy fire-bar overlap     OK (R4 subset)
  walk_verdict_ledger_v2 (B948): cluster_id (BR-1, CC-2, ...)        OK (125/219)
  Sharpe-signature axis: REQUIRES R5 data; NULL pre-R5 (honest)      DEFERRED
  Build APPROVED.

METHODOLOGY (4 axes per PATH §13.3 + honest pre-R5 framing):
  Axis 1 - family_cluster_id from walk_verdict_ledger_v2 ledger
           (e.g., BR-1 breakout-retest, CC-2 candle-confluence). The
           Stage 4 walk taxonomy is the human-curated cluster ground-truth.
  Axis 2 - signal_overlap_neighbors: top-3 strategies by signals_required
           Jaccard (Section 1 reuse). Heuristic for 'reads the same
           producer outputs'.
  Axis 3 - regime_bias_neighbors: top-3 strategies whose regime_affinity
           set matches (Section 5 reuse). Heuristic for 'fires in the
           same regimes'.
  Axis 4 - sharpe_signature_axis: NULL pre-R5. Status string documents
           the gap; column upgrades post-R5 without schema change.
  Composite - closest_passing_neighbor: the strategy with the highest
           combined signal+regime score among same-family-cluster peers
           (or NULL if no same-family peers in roster).

OUTPUT SCHEMA per strategy:
{
  "family_cluster_id": str | None,             # Axis 1 (B948 ledger)
  "cluster_prefix": str | None,                # Axis 1 coarsening (BR/CC/CP/EV/A/ICT/P/SM/T/W)
  "signal_overlap_neighbors": [                 # Axis 2 (B951 Section 1)
    {"strategy": str, "signal_jaccard": float, "shared_signals": int}
  ],
  "regime_bias_neighbors": [                    # Axis 3 (B953 Section 5)
    {"strategy": str, "regime_match": str, "regime_overlap_pct": float}
  ],
  "closest_passing_neighbor": str | None,       # composite top-1
  "closest_neighbor_composite_score": float | None,
  "sharpe_signature_axis_status": str,          # Axis 4 honest NULL
  "method": "static_3_axis_pre_r5",
  "source": "Section 1 signals_required + Section 5 regime_affinity + B948 walk_verdict_ledger_v2",
  "limitation": str,
  "memory_rule_reference": str,
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
WALK_LEDGER_PATH = REPO / "output_audit" / "walk_verdict_ledger_v2.json"

# Composite weighting: signal-overlap is more deterministic than regime-bias
# (regimes are coarse 4-bucket sets; many strategies share the same bucket).
SIGNAL_WEIGHT = 0.6
REGIME_WEIGHT = 0.4
TOP_K = 3


@lru_cache(maxsize=1)
def _load_family_cluster_index() -> dict[str, str]:
    """Load strategy -> family_cluster_id from walk_verdict_ledger_v2.

    Returns dict mapping strategy name to cluster_id (e.g., 'BR-1', 'CC-2').
    Strategies not in the ledger return absent -> None at caller.
    """
    if not WALK_LEDGER_PATH.exists():
        logger.warning("walk_verdict_ledger_v2.json not found at %s", WALK_LEDGER_PATH)
        return {}
    try:
        with open(WALK_LEDGER_PATH) as f:
            data = json.load(f)
    except Exception as e:
        logger.error("Cannot parse walk_verdict_ledger_v2.json: %s", e)
        return {}
    ledger = data.get("ledger", {})
    index: dict[str, str] = {}
    for strategy, entries in ledger.items():
        if not isinstance(entries, list) or not entries:
            continue
        # Take the FIRST cluster_id (entries for the same strategy share it
        # by construction in B948 ledger v2).
        cluster_id = entries[0].get("cluster_id")
        if cluster_id:
            index[strategy] = cluster_id
    return index


@lru_cache(maxsize=1)
def _load_signal_jaccard_matrix() -> dict[str, dict[str, tuple[float, int]]]:
    """Compute pairwise signal-overlap Jaccard from Section 1 signals_required.

    Returns {strategy_a: {strategy_b: (jaccard, shared_count), ...}, ...}
    Reuses Section 1 extractor; static AST scan source.
    """
    try:
        from .section_01_wiring_trace import _parse_screener_for_strategy_signal_deps
    except Exception as e:
        logger.error("Cannot import Section 1 helper: %s", e)
        return {}
    deps = _parse_screener_for_strategy_signal_deps()
    if not deps:
        return {}
    # Build frozenset per strategy
    sets: dict[str, frozenset] = {s: frozenset(sigs) for s, sigs in deps.items()}
    strategies = sorted(sets.keys())
    matrix: dict[str, dict[str, tuple[float, int]]] = {s: {} for s in strategies}
    for i, sa in enumerate(strategies):
        a = sets[sa]
        if not a:
            continue
        for sb in strategies[i + 1:]:
            b = sets[sb]
            if not b:
                continue
            inter = a & b
            if not inter:
                continue
            union = a | b
            j = len(inter) / len(union)
            shared = len(inter)
            matrix[sa][sb] = (j, shared)
            matrix[sb][sa] = (j, shared)
    return matrix


@lru_cache(maxsize=1)
def _load_regime_affinity_index() -> dict[str, frozenset]:
    """Load strategy -> frozenset(regimes) from Section 5 extractor.

    Strategies without explicit entry default to ALLOW-ALL (all 4 regimes).
    """
    try:
        from .section_05_regime_affinity_lineage import _parse_regime_selector_strategy_index
    except Exception as e:
        logger.error("Cannot import Section 5 helper: %s", e)
        return {}
    raw = _parse_regime_selector_strategy_index()
    return {strat: frozenset(entry.get("regimes", [])) for strat, entry in raw.items()}


def _regime_overlap(a: frozenset, b: frozenset) -> tuple[str, float]:
    """Compute regime overlap label + percent between two regime sets.

    Returns (match_label, overlap_pct):
      - 'identical' / 1.0  : same regime set
      - 'subset' / pct     : one is strict subset of the other
      - 'partial' / pct    : intersection but not subset
      - 'disjoint' / 0.0   : no intersection
    Uses |intersection| / |union| as the percent (Jaccard on regime sets).
    """
    if not a and not b:
        return ("no_explicit_entry_both", 0.0)
    if not a or not b:
        return ("no_explicit_entry_one", 0.0)
    if a == b:
        return ("identical", 1.0)
    inter = a & b
    if not inter:
        return ("disjoint", 0.0)
    pct = len(inter) / len(a | b)
    if a.issubset(b) or b.issubset(a):
        return ("subset", round(pct, 4))
    return ("partial", round(pct, 4))


def extract_section_19_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 19 closest_neighbor_cluster for a single strategy.

    Returns dict for Section 19 dossier slot. method='static_3_axis_pre_r5'.
    Sharpe-signature axis is intentionally NULL pre-R5.
    """
    family_index = _load_family_cluster_index()
    signal_matrix = _load_signal_jaccard_matrix()
    regime_index = _load_regime_affinity_index()

    family_cluster_id = family_index.get(strategy)
    # Cluster-prefix coarsening: 'BR-1' -> 'BR' for P4 stratification fallback
    # when per-cluster singletons make same-family neighbor selection useless.
    cluster_prefix = None
    if family_cluster_id and "-" in family_cluster_id:
        cluster_prefix = family_cluster_id.split("-")[0]
    elif family_cluster_id:
        cluster_prefix = family_cluster_id

    # Axis 2: signal-overlap neighbors top-3
    signal_neighbors_raw = signal_matrix.get(strategy, {})
    signal_sorted = sorted(
        signal_neighbors_raw.items(),
        key=lambda x: x[1][0],
        reverse=True,
    )[:TOP_K]
    signal_overlap_neighbors = [
        {
            "strategy": s,
            "signal_jaccard": round(j, 4),
            "shared_signals": shared,
        }
        for s, (j, shared) in signal_sorted
    ]

    # Axis 3: regime-bias neighbors top-3 (compare against all strategies)
    own_regimes = regime_index.get(strategy, frozenset())
    regime_scored: list[tuple[str, str, float]] = []
    for other, other_regimes in regime_index.items():
        if other == strategy:
            continue
        label, pct = _regime_overlap(own_regimes, other_regimes)
        if pct > 0:
            regime_scored.append((other, label, pct))
    regime_scored.sort(key=lambda x: x[2], reverse=True)
    regime_bias_neighbors = [
        {
            "strategy": s,
            "regime_match": label,
            "regime_overlap_pct": pct,
        }
        for s, label, pct in regime_scored[:TOP_K]
    ]

    # Composite: highest combined signal + regime score among same-family peers
    closest_passing_neighbor: str | None = None
    composite_score: float | None = None
    if family_cluster_id is not None:
        same_family = {s for s, cid in family_index.items() if cid == family_cluster_id and s != strategy}
        if same_family:
            best_score = -1.0
            best_peer = None
            for peer in same_family:
                sig_j = signal_neighbors_raw.get(peer, (0.0, 0))[0]
                reg_pair = _regime_overlap(own_regimes, regime_index.get(peer, frozenset()))
                reg_pct = reg_pair[1]
                score = SIGNAL_WEIGHT * sig_j + REGIME_WEIGHT * reg_pct
                if score > best_score:
                    best_score = score
                    best_peer = peer
            closest_passing_neighbor = best_peer
            composite_score = round(best_score, 4) if best_peer else None

    return {
        "family_cluster_id": family_cluster_id,
        "cluster_prefix": cluster_prefix,
        "signal_overlap_neighbors": signal_overlap_neighbors,
        "regime_bias_neighbors": regime_bias_neighbors,
        "closest_passing_neighbor": closest_passing_neighbor,
        "closest_neighbor_composite_score": composite_score,
        "sharpe_signature_axis_status": (
            "NULL_PRE_R5: sharpe-signature axis requires R5 cube per-regime "
            "Sharpe distribution per strategy. Section 9 R4 metrics are too "
            "sparse (127 strategies absent from R4 cube). Column upgrades "
            "post-R5 launch without schema change; populate via R5 trade logs."
        ),
        "method": "static_3_axis_pre_r5",
        "source": (
            "Section 1 signals_required (B951) + Section 5 regime_affinity "
            "(B953) + B948 walk_verdict_ledger_v2 cluster_id"
        ),
        "limitation": (
            "Pre-R5 heuristic clustering. closest_passing_neighbor is bounded "
            "to same family_cluster_id peers; strategies without family-cluster "
            "membership (post-walk roster additions / un-walked) return NULL. "
            "EMPIRICAL CAVEAT discovered at build: B948 walk_verdict_ledger_v2 "
            "has 128 unique cluster_ids across 130 strategy mappings (only "
            "CC-5 and CC-6 contain 2 members each; remainder are singletons). "
            "This means closest_passing_neighbor is NULL for ~99% of strategies "
            "even when family_cluster_id is populated. P4 stratification can "
            "still use family_cluster_id as the categorical sampling axis (cluster "
            "prefix BR-/CC-/CP-/EV-/A-/etc. is meaningful), but per-strategy "
            "closest-neighbor selection requires either (a) coarsening to "
            "cluster_prefix (BR vs CC vs CP) or (b) post-R5 sharpe-signature "
            "axis to bridge same-prefix strategies. Surfaced as Section 19 "
            "finding for P4 design decision. Composite weights (0.6 signal / "
            "0.4 regime) are heuristic and DOCUMENTED, not optimized."
        ),
        "memory_rule_reference": (
            "Council 65 (B960): Section 19 PATH-load-bearing for P4 stratification. "
            "Honest pre-R5 framing per Council 64 anti-iteration mandate "
            "(feedback_audit_recommendations_against_existing_directives)."
        ),
    }


def populate_section_19_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 19 closest_neighbor_cluster slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_19_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_19_closest_neighbor_cluster"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
