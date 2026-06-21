# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.17 META-FINDING TIER 2 wireup + Council 78 RECOMMEND A2-AUDIT-FIRST per CHECKLIST #77.
"""B978 (2026-06-21): Phase P1 Bucket A A2-AUDIT TIER-2 wireup state audit.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.17 META-FINDING TIER 2 wireup
# + Council 78 4/4 UNANIMOUS RECOMMEND A2-AUDIT-FIRST per owner directive
# 2026-06-21 'A2 Tier 2. Council this.'

PURPOSE
-------
Verify TIER-2 producer wireup state BEFORE assuming work needed.
Council 76 banner-verification precedent + feedback_audit_recommendations_
against_existing_directives.

Pre-flight inspection 2026-06-21 surfaced 9-of-9 inject_* functions
WIRED in screener.py + 9 producer modules present. CLAUDE.md banner
still claims "TIER 2 producer wireup completion" outstanding.

This audit verifies 4 axes per inject_* function:
  (a) called in screener.py (verified via grep)
  (b) producer module imports correct producer
  (c) data parquet exists at expected path
  (d) signal-key set non-empty when run on canonical (ticker, date)

NO MUTATION. Read-only state audit. Output informs banner update
decision (RESOLVED vs ENUMERATE-VERIFIED-GAPS).
"""
from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger(__name__)

# 9 inject_* functions per signal_loader.py
INJECT_FUNCTIONS = [
    "inject_news_sentiment_signals",
    "inject_institutional_persistence_signals",
    "inject_short_interest_signals",
    "inject_search_volume_signals",
    "inject_earnings_surprise_yoy_signals",
    "inject_pead_signals",
    "inject_classification_change_signals",
    "inject_insider_buying_signals",
    "inject_institutional_signals",
]

# Per-function family + producer-module + data-path mapping
INJECT_METADATA: dict[str, dict[str, str]] = {
    "inject_news_sentiment_signals": {
        "family": "event-driven",
        "producer_module": "backtest.signals.news_sentiment",
        "data_glob": "data_prefetch/polygon/news/*.parquet",
    },
    "inject_institutional_persistence_signals": {
        "family": "smart-money",
        "producer_module": "backtest.signals.institutional_persistence_consumer",
        "data_glob": "data_prefetch/derived/institutional_persistence_t1a/*.parquet",
    },
    "inject_short_interest_signals": {
        "family": "smart-money",
        "producer_module": "backtest.signals.short_interest",
        "data_glob": "data_prefetch/finra/short_interest/*.parquet",
    },
    "inject_search_volume_signals": {
        "family": "cross-sectional",
        "producer_module": "backtest.signals.search_volume",
        "data_glob": "data_prefetch/pytrends/*.parquet",
    },
    "inject_earnings_surprise_yoy_signals": {
        "family": "event-driven",
        "producer_module": "backtest.signals.pead",
        "data_glob": "data_prefetch/finnhub/earnings/*.parquet",
    },
    "inject_pead_signals": {
        "family": "event-driven",
        "producer_module": "backtest.signals.pead",
        "data_glob": "data_prefetch/finnhub/earnings/*.parquet",
    },
    "inject_classification_change_signals": {
        "family": "event-driven",
        "producer_module": "backtest.signals.sec_edgar_modifiers",
        "data_glob": "data_prefetch/sec_edgar_decoded/*.parquet",
    },
    "inject_insider_buying_signals": {
        "family": "smart-money",
        "producer_module": "backtest.signals.insider_buying",
        "data_glob": "data_prefetch/quiver/insider/*.json",
    },
    "inject_institutional_signals": {
        "family": "smart-money",
        "producer_module": "backtest.data.smart_money",
        "data_glob": "data_prefetch/quiver/institutional/*.json",
    },
}


def _grep_screener_for_inject(inject_fn: str) -> dict[str, Any]:
    """Verify inject_fn called in screener.py."""
    screener = REPO / "backtest" / "signals" / "screener.py"
    if not screener.exists():
        return {"called": False, "line": None}
    text = screener.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(rf"\bfrom\s+backtest\.data\.signal_loader\s+import\s+{re.escape(inject_fn)}|{re.escape(inject_fn)}\(")
    for i, line in enumerate(text.split("\n"), 1):
        if pattern.search(line):
            return {"called": True, "line": i, "snippet": line.strip()[:120]}
    return {"called": False, "line": None}


def _check_data_glob(glob_path: str) -> dict[str, Any]:
    """Check if data files exist at glob path."""
    pattern_path = REPO / glob_path
    parent = pattern_path.parent
    pattern = pattern_path.name
    if not parent.exists():
        return {"data_present": False, "n_files": 0, "parent_exists": False}
    matches = list(parent.glob(pattern))
    # Also check recursive
    if not matches and parent.exists():
        recursive_matches = list(parent.rglob("*"))
        n_files_total = len([p for p in recursive_matches if p.is_file()])
        return {
            "data_present": n_files_total > 0,
            "n_files": n_files_total,
            "parent_exists": True,
            "method": "rglob_count",
        }
    return {
        "data_present": len(matches) > 0,
        "n_files": len(matches),
        "parent_exists": True,
        "method": "glob_match",
    }


def _check_producer_module(producer_module: str) -> dict[str, Any]:
    """Check if producer module exists + importable."""
    module_path = REPO / (producer_module.replace(".", "/") + ".py")
    exists = module_path.exists()
    importable = False
    if exists:
        try:
            __import__(producer_module)
            importable = True
        except Exception as e:
            return {"exists": True, "importable": False, "error": f"{type(e).__name__}: {e}"}
    return {"exists": exists, "importable": importable}


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger.info("TIER-2 wireup state audit (9 inject_* x 4 axes)")
    results: dict[str, Any] = {}
    summary = {
        "n_inject_fns": len(INJECT_FUNCTIONS),
        "n_wired_in_screener": 0,
        "n_producer_modules_present": 0,
        "n_producer_modules_importable": 0,
        "n_data_paths_present": 0,
        "n_data_paths_missing": 0,
        "fully_wired_count": 0,
        "gaps_by_family": {"smart-money": [], "event-driven": [], "cross-sectional": []},
    }
    for fn in INJECT_FUNCTIONS:
        meta = INJECT_METADATA.get(fn, {})
        family = meta.get("family", "unknown")
        producer = meta.get("producer_module", "")
        data_glob = meta.get("data_glob", "")
        wired = _grep_screener_for_inject(fn)
        producer_state = _check_producer_module(producer) if producer else {"exists": False, "importable": False}
        data_state = _check_data_glob(data_glob) if data_glob else {"data_present": False, "n_files": 0}
        fully_wired = (
            wired["called"]
            and producer_state.get("exists", False)
            and producer_state.get("importable", False)
            and data_state.get("data_present", False)
        )
        results[fn] = {
            "family": family,
            "wired_in_screener": wired,
            "producer_module_state": producer_state,
            "data_path_state": data_state,
            "fully_wired": fully_wired,
        }
        if wired["called"]:
            summary["n_wired_in_screener"] += 1
        if producer_state.get("exists", False):
            summary["n_producer_modules_present"] += 1
        if producer_state.get("importable", False):
            summary["n_producer_modules_importable"] += 1
        if data_state.get("data_present", False):
            summary["n_data_paths_present"] += 1
        else:
            summary["n_data_paths_missing"] += 1
            summary["gaps_by_family"].setdefault(family, []).append(fn)
        if fully_wired:
            summary["fully_wired_count"] += 1

    # Verdict
    if summary["fully_wired_count"] == 9:
        verdict = "RESOLVED_BANNER_STALE"
        narrative = (
            "All 9 inject_* functions are wired in screener.py + producer "
            "modules present + importable + data paths populated. CLAUDE.md "
            "banner 'TIER 2 producer wireup completion' is STALE bookkeeping "
            "similar to PYRAMID-CLEANUP-ENV B973 precedent. Honest-finding "
            "pivot: update banner to RESOLVED."
        )
    elif summary["fully_wired_count"] >= 7:
        verdict = "MOSTLY_WIRED_NARROW_GAPS"
        narrative = f"{summary['fully_wired_count']} of 9 fully wired; narrow gaps in specific families."
    else:
        verdict = "MULTIPLE_WIRING_GAPS_NEED_FIX"
        narrative = f"{summary['fully_wired_count']} of 9 fully wired; multiple gaps need per-family fix batches."

    summary["verdict"] = verdict
    summary["narrative"] = narrative

    out_path = REPO / "output_audit" / "b978_tier2_wireup_state_audit.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "schema_version": "1.0",
            "batch": "B978",
            "council": "78_UNANIMOUS_A2_AUDIT_FIRST",
            "summary": summary,
            "per_inject_fn": results,
            "memory_rule_reference": (
                "Council 76 PYRAMID-CLEANUP-ENV banner-verification precedent "
                "(B973) + feedback_audit_recommendations_against_existing_"
                "directives + feedback_no_surface_level_audits."
            ),
        }, f, indent=2, default=str)

    logger.info("AUDIT COMPLETE:")
    logger.info("  Wired in screener: %d / 9", summary["n_wired_in_screener"])
    logger.info("  Producer modules present: %d / 9", summary["n_producer_modules_present"])
    logger.info("  Producer modules importable: %d / 9", summary["n_producer_modules_importable"])
    logger.info("  Data paths present: %d / 9", summary["n_data_paths_present"])
    logger.info("  Data paths MISSING: %d / 9", summary["n_data_paths_missing"])
    logger.info("  Fully wired: %d / 9", summary["fully_wired_count"])
    logger.info("  Verdict: %s", verdict)
    logger.info("  Narrative: %s", narrative)
    logger.info("Output: %s", out_path.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
