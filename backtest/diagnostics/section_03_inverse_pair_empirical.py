# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 3 per CHECKLIST #77.
"""B961 (2026-06-20): Phase P1 batch 21 - Section 3 inverse_pair_empirical extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 3 + Council 66 verdict
# per owner directive 2026-06-20 'Continue, council this' per CHECKLIST #77.

PURPOSE
-------
Section 3 = empirical inverse-pair probe (NOT literature speculation).

PATH Section 13.3 row 3 spec:
  'Empirical inverse-pair probe (NOT literature)
   Mechanical inverse, measure fire-count + crude WR; NOT literature
   speculation'

Council 60 finding-addressing pivot: addresses 25 B956 INVERSE_UNSAFE
findings directly.

PRE-BUILD CHECK (Council 66 mandate, executed before coding):
  ALL_STRATEGIES roster: 219 strategies                        OK
  Suffix distribution:
    _long suffix:    91
    _short suffix:   45
    Neither suffix:  83 (e.g., smc_bos_continuation, xs_momentum_*)
  Long with matching Short pair: 13 (canonical pairs)
  Long without matching Short: 78
  R4 trade_log: ticker + strategy + entry_date + direction + pnl_pct   OK
  Section 8 (B955) asymmetric_data_source data:                        OK
  Build APPROVED.

METHODOLOGY (Council 66 honest framing - per `feedback_per_strategy_deep_dive_stage4`):
  Axis 1 - Canonical name-pattern detection:
    - 'strat_X_long' -> 'strat_X_short' candidate
    - 'strat_X_short' -> 'strat_X_long' candidate
    - Neither-suffix names: no canonical inverse (explicit flag)

  Axis 2 - Registry existence check:
    - inverse_candidate in ALL_STRATEGIES?

  Axis 3 - R4 fire-count cross-reference:
    - self_r4_fires: count of R4 entries for this strategy
    - inverse_r4_fires: count for inverse (if exists)

  Axis 4 - Asymmetric-data-source flag (Section 8 reuse):
    - mechanical_inverse_unsafe flag from B955 Section 8
    - If True, inverse may be ECONOMICALLY false (13F long-only, etc.)

  Per `feedback_asymmetric_data_sources_break_mechanical_inverse` (B611):
    Don't propose mechanical mirror on regulatory-disclosure-asymmetric
    data sources.

OUTPUT SCHEMA per strategy:
{
  "has_named_inverse_candidate": bool,
  "inverse_candidate_name": str | None,
  "inverse_exists_in_registry": bool,
  "self_r4_fires": int | None,
  "inverse_r4_fires": int | None,
  "self_in_r4_cube": bool,
  "inverse_in_r4_cube": bool,
  "asymmetric_data_source_flag": bool,
  "b956_inverse_unsafe_flag": bool,
  "asymmetric_sources": [list from Section 8],
  "inverse_recommendation": str,  # 'pair_exists' / 'missing_inverse_candidate'
                                    # / 'asymmetric_data_no_mirror' / 'no_canonical_inverse'
  "method": "static_name_pattern_plus_r4_fire_count_plus_section_8",
  "memory_rule_reference": str,
  "limitation": str,
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


@lru_cache(maxsize=1)
def _load_all_strategies() -> frozenset[str]:
    """Load ALL_STRATEGIES roster as frozenset for fast membership checks."""
    from backtest.signals.screener import ALL_STRATEGIES
    return frozenset(ALL_STRATEGIES.keys())


@lru_cache(maxsize=1)
def _load_r4_fire_counts() -> dict[str, int]:
    """Load per-strategy R4 fire count (unique (ticker, entry_date) pairs)."""
    if not R4_TRADE_DETAIL_CSV.exists():
        return {}
    try:
        import pandas as pd
        df = pd.read_csv(R4_TRADE_DETAIL_CSV, usecols=["strategy", "ticker", "entry_date"])
        df = df.drop_duplicates()
        counts = df.groupby("strategy").size().to_dict()
        return counts
    except Exception as e:
        logger.error("Cannot load R4 trade_exit_detail.csv: %s", e)
        return {}


def _canonical_inverse_candidate(strategy: str) -> str | None:
    """Compute canonical inverse name candidate from strategy name.

    Pattern:
      'strat_X_long' -> 'strat_X_short'
      'strat_X_short' -> 'strat_X_long'
      'X_long' -> 'X_short'  (post-prefix-strip form)
      'X_short' -> 'X_long'
      Neither suffix -> None (no canonical inverse; needs owner-walk)
    """
    if strategy.endswith("_long"):
        return strategy[:-len("_long")] + "_short"
    if strategy.endswith("_short"):
        return strategy[:-len("_short")] + "_long"
    return None


def extract_section_03_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 3 inverse_pair_empirical for a single strategy."""
    all_strategies = _load_all_strategies()
    r4_fires = _load_r4_fire_counts()

    inverse_candidate = _canonical_inverse_candidate(strategy)
    has_inverse_candidate = inverse_candidate is not None
    inverse_exists = bool(inverse_candidate and inverse_candidate in all_strategies)

    self_in_r4 = strategy in r4_fires
    inverse_in_r4 = bool(inverse_candidate and inverse_candidate in r4_fires)
    self_r4_fires = r4_fires.get(strategy)
    inverse_r4_fires = r4_fires.get(inverse_candidate) if inverse_candidate else None

    # Cross-reference Section 8 (B955) for asymmetric_data_source flag
    asymmetric_flag = False
    b956_inverse_unsafe = False
    asymmetric_sources: list[str] = []
    try:
        from backtest.diagnostics.section_08_data_source_asymmetry import (
            extract_section_08_for_strategy,
        )
        s8 = extract_section_08_for_strategy(strategy)
        asymmetric_sources = s8.get("asymmetric_sources", [])
        asymmetric_flag = bool(asymmetric_sources)
        b956_inverse_unsafe = s8.get("mechanical_inverse_unsafe", False)
    except Exception as e:
        logger.debug("Section 8 lookup failed for %s: %s", strategy, e)

    # Recommendation logic
    if b956_inverse_unsafe:
        recommendation = "asymmetric_data_no_mirror"
        # B611: regulatory-disclosure asymmetric data; mechanical mirror is wrong
    elif not has_inverse_candidate:
        recommendation = "no_canonical_inverse"
        # Neither _long nor _short suffix; needs owner-walk for inverse logic
    elif inverse_exists:
        recommendation = "pair_exists"
        # Both sides registered
    else:
        recommendation = "missing_inverse_candidate"
        # _long without _short OR _short without _long; potential Class 7 NEW

    return {
        "has_named_inverse_candidate": has_inverse_candidate,
        "inverse_candidate_name": inverse_candidate,
        "inverse_exists_in_registry": inverse_exists,
        "self_r4_fires": self_r4_fires,
        "inverse_r4_fires": inverse_r4_fires,
        "self_in_r4_cube": self_in_r4,
        "inverse_in_r4_cube": inverse_in_r4,
        "asymmetric_data_source_flag": asymmetric_flag,
        "b956_inverse_unsafe_flag": b956_inverse_unsafe,
        "asymmetric_sources": asymmetric_sources,
        "inverse_recommendation": recommendation,
        "method": "static_name_pattern_plus_r4_fire_count_plus_section_8",
        "memory_rule_reference": (
            "feedback_asymmetric_data_sources_break_mechanical_inverse (B611): "
            "When asymmetric_data_source_flag=True (13F long-only, insider buy, "
            "SC 13D), mechanical mirror is economically false. Recommendation "
            "asymmetric_data_no_mirror overrides naming-pattern logic."
        ),
        "limitation": (
            "Name-pattern detection covers _long/_short suffix only. 83 strategies "
            "have neither suffix (e.g., smc_bos_continuation, xs_momentum_top_decile); "
            "their inverse logic is non-canonical and flagged as 'no_canonical_inverse'. "
            "Owner-walk required to define inverse semantics for these."
        ),
    }


def populate_section_03_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 3 inverse_pair_empirical slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_03_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_03_inverse_pair_empirical"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
