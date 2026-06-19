"""B935 (2026-06-19): Section 9 TWO-TRACK R4 cube metrics extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 + Council 44 batch 1 commit 3 +
# Council 45 owner-A TWO-TRACK design per owner directive 2026-06-19 Option A.

PURPOSE
-------
Per Council 45 owner-approved architecture:

  TRACK 1: R4-included strategies (~102 in output_batch395_final/)
    - Populate metrics from backtest_results.csv
    - All canonical PASSING_CRITERIA fields (sharpe / sortino / calmar /
      PF / max_DD / total_ROI / WR / DSR / chow / ADF / cost-sensitivity)
    - Per-regime verdicts
    - r4_status = "in_r4_cube"
    - r5_inclusion_criterion contribution: "r4_metrics_passed" candidate

  TRACK 2: Post-R4 additions (~117 strategies in current ALL_STRATEGIES
           but NOT in R4 output)
    - Section 9 value = {
        "r4_status": "post_r4_addition",
        "metrics": null,
        "evidence_source": "section_9b",
        "added_after_r4": True
      }
    - Strategy's pre-cube evidence flows through Section 9b extractor
      (built in subsequent batch B936+)
    - r5_inclusion_criterion contribution: "pre_cube_evidence_sufficient"
      candidate

OUTPUTS
-------
- Updates dossier.json sections.section_09_r4_cube_metrics with structured dict
- Sets dossier.r5_inclusion_criterion_section_9 hint (combined with 9b later)

USAGE
-----
    from backtest.diagnostics.section_09_r4_cube_metrics import extract_section_09
    section_9_value = extract_section_09("donchian_10_breakout")
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)


REPO = Path(__file__).resolve().parent.parent.parent
R4_RESULTS_CSV = REPO / "output_batch395_final" / "backtest_results.csv"


# Canonical metric columns to extract from R4 CSV per PASSING_CRITERIA + Council 38.
R4_METRIC_COLUMNS = [
    "total_trades",
    "win_rate", "win_rate_ci_low", "win_rate_ci_high",
    "profit_factor",
    "expected_value",
    "win_loss_ratio",
    "avg_win_pct", "avg_loss_pct",
    "max_drawdown_pct",
    "total_roi_pct",
    "sharpe_ratio", "sharpe_daily",
    "sortino_ratio",
    "deflated_sharpe",
    "psr",
    "calmar_ratio",
    "kelly",
    "avg_hold_days",
    "best_trade_pct", "worst_trade_pct",
    # AUTO-FAIL diagnostics
    "sharpe_at_0bps", "sharpe_at_5bps", "sharpe_at_10bps", "sharpe_at_20bps",
    "adf_statistic", "adf_p_value", "is_stationary",
    "chow_f_statistic", "chow_p_value", "has_structural_break",
    # Smart-money + macro
    "smart_money_lift",
    "macro_correlation",
    # Per-regime
    "regimes_profitable",
    "best_regimes",
    # Pass/fail summary
    "passes_all",
]


_R4_DATAFRAME_CACHE: Optional[pd.DataFrame] = None


def _load_r4_dataframe() -> pd.DataFrame:
    """Lazy-load + cache the R4 results CSV across multiple section_9 calls."""
    global _R4_DATAFRAME_CACHE
    if _R4_DATAFRAME_CACHE is not None:
        return _R4_DATAFRAME_CACHE
    if not R4_RESULTS_CSV.exists():
        _R4_DATAFRAME_CACHE = pd.DataFrame()
        return _R4_DATAFRAME_CACHE
    df = pd.read_csv(R4_RESULTS_CSV)
    _R4_DATAFRAME_CACHE = df
    return df


def extract_section_09(strategy: str) -> dict[str, Any]:
    """Extract Section 9 TWO-TRACK value for a strategy.

    Returns a dict matching Council 45 schema:

    TRACK 1 (in R4):
        {
          "r4_status": "in_r4_cube",
          "track": 1,
          "metrics": { <R4_METRIC_COLUMNS> },
          "r5_inclusion_criterion_hint": "r4_metrics_passed_candidate",
          "added_after_r4": False,
        }

    TRACK 2 (post-R4 addition):
        {
          "r4_status": "post_r4_addition",
          "track": 2,
          "metrics": null,
          "evidence_source": "section_9b",
          "r5_inclusion_criterion_hint": "pre_cube_evidence_sufficient_candidate",
          "added_after_r4": True,
        }
    """
    df = _load_r4_dataframe()
    if df.empty or "strategy" not in df.columns:
        return {
            "r4_status": "r4_csv_missing",
            "track": 0,
            "metrics": None,
            "r5_inclusion_criterion_hint": "deferred",
            "added_after_r4": None,
            "error": f"R4 results CSV unavailable: {R4_RESULTS_CSV}",
        }

    sub = df[df["strategy"] == strategy]
    if sub.empty:
        # TRACK 2: Post-R4 addition
        return {
            "r4_status": "post_r4_addition",
            "track": 2,
            "metrics": None,
            "evidence_source": "section_9b",
            "r5_inclusion_criterion_hint": "pre_cube_evidence_sufficient_candidate",
            "added_after_r4": True,
        }

    # TRACK 1: In R4 cube - extract metrics
    row = sub.iloc[0]
    metrics = {}
    for col in R4_METRIC_COLUMNS:
        if col not in df.columns:
            metrics[col] = None
            continue
        val = row[col]
        if pd.isna(val):
            metrics[col] = None
        elif isinstance(val, (int, float)):
            metrics[col] = float(val) if not (val != val) else None  # NaN -> None
        else:
            metrics[col] = str(val)

    # Determine r5_inclusion_criterion_hint from R4 passes_all
    passes_all = metrics.get("passes_all")
    if isinstance(passes_all, str):
        passes_all = passes_all.strip().lower() == "true"
    hint = (
        "r4_metrics_passed_candidate" if passes_all
        else "r4_metrics_failed_candidate"
    )

    return {
        "r4_status": "in_r4_cube",
        "track": 1,
        "metrics": metrics,
        "r5_inclusion_criterion_hint": hint,
        "added_after_r4": False,
    }


def populate_section_09_for_dossier(strategy: str, dossier_path: Path) -> Path:
    """Read dossier.json, set Section 9, write back. Returns dossier_path."""
    if not dossier_path.exists():
        raise FileNotFoundError(f"Dossier not initialized: {dossier_path}")
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_value = extract_section_09(strategy)
    # Section 9 key per DOSSIER_SECTIONS naming convention
    dossier["sections"]["section_09_r4_cube_metrics"] = section_value
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
    logger.debug("Populated Section 9 for %s -> %s", strategy, section_value.get("r4_status"))
    return dossier_path
