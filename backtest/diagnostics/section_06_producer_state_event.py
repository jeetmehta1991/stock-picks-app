"""B937 (2026-06-19): Section 6 producer STATE/EVENT classification extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 6 + Council 46 batch 2
# commit 2 per owner directive 2026-06-19 Option A. Per memory rule
# `feedback_signal_temporality_event_vs_state` (2026-06-07 B611 lesson).

PURPOSE
-------
For each strategy, extract the signals it consumes via AST + s.get("...") scan,
then classify each signal as:
  - EVENT: bar-of-fire trigger (price break, candle pattern, EVENT-anchored
    lookback). Provides timing alpha.
  - STATE: slow background filter (13F quarterly + 45d lag, trend filter
    via long EMA, regime classification). Provides eligibility, NOT timing.
  - UNKNOWN: unclassified; needs manual review

Per memory rule `feedback_signal_temporality_event_vs_state`:
    "Slow background states (quarterly 13F, financial statements) don't
    provide timing alpha at bar of fire. Strategies that credit STATE
    signals with 'smart-money sponsorship' / 'conviction timing'
    mis-attribute alpha."

HEURISTICS (per Council 46 First Principles design)
---------------------------------------------------
EVENT signals: name contains _recent_Nd / _break / _today / _cross / _spike /
               _retest / _confirm / _signal_today
STATE signals: name from quarterly/annual data source (13F + insider 30d
               lookback + financials + persistence + classification + sector)
UNKNOWN: ambiguous (rsi_14, price_above_ema, vol_above_avg without _today suffix)

Manual override JSON (per Council 46 design):
    dossier_signal_temporality_overrides.json
    Format: {signal_name: temporality_label}
    Empty {} initially; populated when reviewer disambiguates.
"""
from __future__ import annotations

import inspect
import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


REPO = Path(__file__).resolve().parent.parent.parent
OVERRIDES_PATH = REPO / "backtest" / "diagnostics" / "dossier_signal_temporality_overrides.json"


# EVENT pattern markers (bar-of-fire triggers)
EVENT_PATTERNS = [
    r"_break(?!_)",          # _break (but not _breakdown_short etc; allow underscores after)
    r"_break_recent_\d+d",   # B655/B721 EVENT-recency pattern
    r"_today\b",             # _today suffix
    r"_cross\b",             # _bullish_cross, _bearish_cross
    r"_spike\b",             # vol_spike etc.
    r"_retest\b",            # _retest events
    r"_breakdown\b",         # bearish break
    r"_breakout\b",          # bullish break
    r"_flip_recent",         # supertrend_flip_recent_long_5d
    r"_blowoff\b",           # B643 redesign
    r"_capitulation\b",      # B643 W5 redesign
    r"_signal_today\b",      # generic EVENT signal
    r"_recent_\d+d",         # institutional_increased_break_recent_5d
]

# STATE pattern markers (slow background; eligibility filter)
STATE_PATTERNS = [
    r"^institutional_",       # 13F-based (quarterly + 45d lag)
    r"^persistence_",         # multi-quarter 13F derived
    r"_persistence_",         # institutional_persistence_*
    r"^classification_",      # GICS reclass (slow events; weeks-to-months)
    r"_classification_",
    r"^insider_",             # 30-day lookback Form 4 = quasi-STATE
    r"^short_interest",       # bi-weekly FINRA
    r"_above_ema_(50|100|200)\b",  # long-EMA trend filter (slow)
    r"^price_above_ema_(50|100|200)\b",
    r"_below_ema_(100|200)\b",     # long EMA below
    r"_above_avwap_\d+",      # AVWAP eligibility filter
    r"^sector_",              # sector-strength comparison (slow)
    r"_within_pead_window\b", # earnings window (slow STATE; lasts 60d)
    r"^bb_squeeze\b",         # Bollinger squeeze (slow)
    r"^committed_growth_holders\b",  # 13F derived
    r"^total_active_holders\b",       # 13F derived
    r"^persistence_quarters_buying\b", # 13F derived
    r"_yoy_growth\b",         # quarterly financials
    r"_with_smart_money\b",   # composite of 13F + insider (slow)
]


def _load_overrides() -> dict[str, str]:
    """Load manual temporality overrides; create empty file if missing."""
    if not OVERRIDES_PATH.exists():
        OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OVERRIDES_PATH, "w") as f:
            json.dump({"__doc__": "B937 manual temporality overrides; map signal_name -> EVENT|STATE|UNKNOWN"}, f, indent=2)
    with open(OVERRIDES_PATH) as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def classify_signal_temporality(signal_name: str, overrides: dict[str, str] = None) -> dict[str, Any]:
    """Classify a single signal as EVENT / STATE / UNKNOWN.

    Returns:
        {
          "temporality": "EVENT" | "STATE" | "UNKNOWN",
          "matched_pattern": <regex that matched, or None>,
          "manual_override": <True if from overrides JSON>,
        }
    """
    if overrides is None:
        overrides = _load_overrides()
    if signal_name in overrides:
        return {
            "temporality": overrides[signal_name],
            "matched_pattern": "<manual_override>",
            "manual_override": True,
        }
    # EVENT patterns first (more specific)
    for pat in EVENT_PATTERNS:
        if re.search(pat, signal_name):
            return {
                "temporality": "EVENT",
                "matched_pattern": pat,
                "manual_override": False,
            }
    # STATE patterns
    for pat in STATE_PATTERNS:
        if re.search(pat, signal_name):
            return {
                "temporality": "STATE",
                "matched_pattern": pat,
                "manual_override": False,
            }
    return {
        "temporality": "UNKNOWN",
        "matched_pattern": None,
        "manual_override": False,
    }


def _extract_consumed_signals(strategy: str) -> list[str]:
    """Extract signal names consumed by strategy via s.get("...") AST scan."""
    try:
        from backtest.signals.screener import ALL_STRATEGIES
    except Exception:
        return []
    fn = ALL_STRATEGIES.get(strategy)
    if fn is None:
        return []
    try:
        src = inspect.getsource(fn)
    except Exception:
        return []
    # Match s.get("signal_name", ...) or signals.get("signal_name", ...)
    matches = re.findall(r'\bs(?:ignals)?\.get\(["\']([^"\']+)["\']', src)
    return sorted(set(matches))


def extract_section_06(strategy: str) -> dict[str, Any]:
    """Extract Section 6 producer STATE/EVENT classification for a strategy.

    Returns:
        {
          "signals_consumed": [...],
          "n_signals": int,
          "classifications": {
              signal_name: {temporality, matched_pattern, manual_override}
          },
          "summary": {
              "n_event": int,
              "n_state": int,
              "n_unknown": int,
              "event_to_state_ratio": float,
              "feedback_signal_temporality_event_vs_state_compliance": bool,
          },
        }

    Per memory rule, strategies that combine STATE signals + claim
    timing alpha violate the compliance check. The dossier flag enables
    Phase D walk reviewers to surface this systematically.
    """
    signals = _extract_consumed_signals(strategy)
    overrides = _load_overrides()
    classifications = {sig: classify_signal_temporality(sig, overrides) for sig in signals}

    n_event = sum(1 for v in classifications.values() if v["temporality"] == "EVENT")
    n_state = sum(1 for v in classifications.values() if v["temporality"] == "STATE")
    n_unknown = sum(1 for v in classifications.values() if v["temporality"] == "UNKNOWN")
    total = max(n_event + n_state + n_unknown, 1)

    # Compliance heuristic: strategy must have AT LEAST 1 EVENT signal for
    # timing alpha attribution (per feedback_signal_temporality_event_vs_state).
    # Pure STATE strategies can be eligibility filters but should not claim
    # "bar-of-fire" timing.
    compliance = n_event >= 1

    return {
        "signals_consumed": signals,
        "n_signals": len(signals),
        "classifications": classifications,
        "summary": {
            "n_event": n_event,
            "n_state": n_state,
            "n_unknown": n_unknown,
            "event_to_state_ratio": round(n_event / total, 3),
            "feedback_signal_temporality_event_vs_state_compliance": compliance,
        },
    }


def populate_section_06_for_dossier(strategy: str, dossier_path: Path) -> Path:
    """Read dossier.json, set Section 6, write back."""
    if not dossier_path.exists():
        raise FileNotFoundError(f"Dossier not initialized: {dossier_path}")
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_value = extract_section_06(strategy)
    dossier["sections"]["section_06_producer_state_event"] = section_value
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
    return dossier_path
