"""B955 (2026-06-20): Phase P1 batch 15 - Section 8 data_source_asymmetry extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 8 + Council 59 UNANIMOUS
# verdict per owner directive 2026-06-20 autonomous mandate + memory rule
# feedback_asymmetric_data_sources_break_mechanical_inverse (B611).

PURPOSE
-------
Section 8 = walk-aid filter for Class 7 NEW_STRATEGY mirror proposals.

Per memory rule feedback_asymmetric_data_sources_break_mechanical_inverse:
  B611 lesson: 13F filings are LONG-ONLY by SEC rule; SC 13D activist
  positions are long-only; insider Form 4 BUYING is a one-sided signal.
  Mechanical inverse strategies on these data sources are ECONOMICALLY
  FALSE. Step 6 missing-inverse audit must include DATA-SOURCE SYMMETRY
  check before proposing Class 7 inverses.

Section 8 surfaces this directly in the dossier: owner reads
mechanical_inverse_unsafe to know if a Class 7 mirror proposal is wrong
BEFORE doing the analysis.

PRE-BUILD CHECK (Council 59 Executor mandate, executed):
  Producer modules for asymmetric data confirmed:
    - backtest/data/smart_money.py (13F + congressional)
    - backtest/signals/insider_buying.py (insider Form 4 buying)
    - backtest/signals/sec_edgar_extractor.py (SC 13D activist)
    - backtest/signals/short_interest.py (one-sided by construction)
    - backtest/signals/pead.py (PEAD; asymmetric event)
  Asymmetric-signal regex patterns confirmed match canonical strategies:
    insider_cluster_long -> insider_cluster_active, insider_unique_buyers_30d
    activist_13d_long -> sc_13d_filed_within_30d, sc_13d_latest_filer_identity
    short_borrow_trap_avoid -> days_to_cover

DESIGN (Council 59 First Principles + Contrarian refinement):
  - SOURCE-CLASS field (list): which asymmetric data classes the strategy reads
    Classes: {13F, insider_buy, 13D, congressional, short_interest, pead_event}
  - mechanical_inverse_unsafe: True ONLY if any source in
    INVERSE_UNSAFE_CLASSES = {13F, insider_buy, 13D}
    (congressional + short_interest + pead_event are asymmetric IN DATA
     but inverse is feasible with complementary signals)
  - reuses B951 Section 1 wiring data (signal-list per strategy)

NOT a verdict driver. Informational tag. Walk-aid filter only.

OUTPUT SCHEMA per strategy:
{
  "asymmetric_sources": [list of source classes],
  "mechanical_inverse_unsafe": bool,
  "signals_triggering_classification": {class: [signals]},
  "method": "static_signal_pattern_match",
  "memory_rule_reference": "feedback_asymmetric_data_sources_break_mechanical_inverse (B611)",
  "is_walk_aid": True,
}
"""
from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent.parent

# Signal-class regex patterns (asymmetric data source classification)
ASYMMETRIC_SIGNAL_PATTERNS = {
    "13F": [
        re.compile(r"^13f_", re.IGNORECASE),
        re.compile(r"^smart_money_13f", re.IGNORECASE),
        re.compile(r"^institutional_(?!holdings|momentum_long|momentum_short).*", re.IGNORECASE),
        re.compile(r"^smart_money_institutional", re.IGNORECASE),
        re.compile(r"^smart_money_concentration", re.IGNORECASE),
    ],
    "insider_buy": [
        re.compile(r"^insider_cluster", re.IGNORECASE),
        re.compile(r"^insider_purchase", re.IGNORECASE),
        re.compile(r"^insider_unique_buyers", re.IGNORECASE),
        re.compile(r"^insider_buying", re.IGNORECASE),
    ],
    "13D": [
        re.compile(r"^sc_13d", re.IGNORECASE),
        re.compile(r"^activist_13d", re.IGNORECASE),
        re.compile(r"^_13d_", re.IGNORECASE),
    ],
    "congressional": [
        re.compile(r"^congressional_", re.IGNORECASE),
        re.compile(r"^pelosi_", re.IGNORECASE),
        re.compile(r"^smart_money_congressional", re.IGNORECASE),
    ],
    "short_interest": [
        re.compile(r"^short_interest", re.IGNORECASE),
        re.compile(r"^days_to_cover$", re.IGNORECASE),
        re.compile(r"^dtc_", re.IGNORECASE),
        re.compile(r"^borrow_", re.IGNORECASE),
        re.compile(r"^short_borrow", re.IGNORECASE),
    ],
    "pead_event": [
        re.compile(r"^pead_", re.IGNORECASE),
        re.compile(r"^earnings_announcement", re.IGNORECASE),
        re.compile(r"^within_pead_window", re.IGNORECASE),
    ],
}

# B611 inverse-unsafe classes: regulatory-disclosure asymmetric
INVERSE_UNSAFE_CLASSES = frozenset({"13F", "insider_buy", "13D"})


@lru_cache(maxsize=1)
def _load_strategy_signal_index() -> dict[str, list[str]]:
    """Load strategy -> signal-list from B951 AST parser."""
    from backtest.diagnostics.section_01_wiring_trace import (
        _parse_screener_for_strategy_signal_deps,
    )
    return _parse_screener_for_strategy_signal_deps()


def classify_signal(signal_key: str) -> list[str]:
    """Return list of asymmetric source classes that match this signal key."""
    matches = []
    for source_class, patterns in ASYMMETRIC_SIGNAL_PATTERNS.items():
        for p in patterns:
            if p.match(signal_key):
                matches.append(source_class)
                break
    return matches


def extract_section_08_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 8 data_source_asymmetry for a single strategy."""
    index = _load_strategy_signal_index()
    signals = index.get(strategy, [])
    sources_to_signals: dict[str, list[str]] = {}
    for sig in signals:
        for cls in classify_signal(sig):
            sources_to_signals.setdefault(cls, []).append(sig)
    asymmetric_sources = sorted(sources_to_signals.keys())
    inverse_unsafe = any(c in INVERSE_UNSAFE_CLASSES for c in asymmetric_sources)
    return {
        "asymmetric_sources": asymmetric_sources,
        "mechanical_inverse_unsafe": inverse_unsafe,
        "signals_triggering_classification": sources_to_signals,
        "inverse_unsafe_classes": sorted(INVERSE_UNSAFE_CLASSES),
        "method": "static_signal_pattern_match",
        "memory_rule_reference": (
            "feedback_asymmetric_data_sources_break_mechanical_inverse (B611): "
            "13F + SC 13D + Form 4 insider buying are regulatory-disclosure "
            "asymmetric (long-only by data source structure). Mechanical "
            "inverse strategies on these sources are economically false. "
            "Congressional + short_interest + PEAD are asymmetric in DATA "
            "but inverse is feasible with complementary signals."
        ),
        "is_walk_aid": True,
    }


def populate_section_08_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 8 data_source_asymmetry slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_08_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_08_data_source_asymmetry"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
