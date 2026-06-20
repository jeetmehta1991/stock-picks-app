"""B954 (2026-06-20): Phase P1 batch 14 - Section 13 exit_axis_best extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 Section 13 + Council 58 UNANIMOUS
# 4/4 verdict per owner directive 2026-06-20 autonomous mandate + Outsider
# tiebreaker 'Stage-5-relevant beats memory-rule-coverage'.

PURPOSE
-------
Section 13 = R4-included strategies' best-exit-method surface for the dossier.
Per Council 58 Outsider: 'directly informs Stage 5 SWAP batches (CLAUDE.md
queue item iii)'.

PRE-BUILD CHECK (Council 56+58 Executor mandate, executed):
  R4 output dir: output_batch395_final/
  exit_strategy_best.csv schema: strategy, exit_method, total_pnl_pct, n,
    win_rate (5 columns)
  Coverage: 72 strategies (of 219 in current roster)
  Distinct exit methods present: 7 (breakeven_plus_trail, chandelier_3x,
    class_time_stop, earnings_blackout, fixed_4r_2r, next_pivot_target,
    r_multiple_2r)
  Ranking metric: total_pnl_pct (NOT Sharpe per CLAUDE.md #10)

HONEST FRAMING (Council 58 First Principles mandate):
  - 147 strategies (of 219) have NULL Section 13 - not in R4 CSV
  - 'Best' is ranked by total_pnl_pct; Sharpe per-cell not in this CSV
  - Only 7 of 26 exit methods appear as winners (other 19 lost or no fires)
  - This is honest 'best per R4' surface; future B-N batch may add per-cell
    Sharpe ranking when R4 re-run with per-exit-method full metrics

OUTPUT SCHEMA per strategy:
{
  "best_exit_method": str | None,
  "best_exit_total_pnl_pct": float | None,
  "best_exit_n_trades": int | None,
  "best_exit_win_rate": float | None,
  "ranking_metric": "total_pnl_pct",
  "in_r4_cube": bool,
  "source": "output_batch395_final/exit_strategy_best.csv",
  "method": "r4_passthrough",
  "limitation": str (HONEST about per-cell-Sharpe unavailability + 147 NULL),
  "stage_5_swap_relevant": bool,
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
R4_BEST_EXIT_CSV = REPO / "output_batch395_final" / "exit_strategy_best.csv"


@lru_cache(maxsize=1)
def _load_r4_best_exit_index() -> dict[str, dict[str, Any]]:
    """Load R4 best-exit CSV indexed by strategy name."""
    if not R4_BEST_EXIT_CSV.exists():
        logger.warning("R4 exit_strategy_best.csv not found at %s", R4_BEST_EXIT_CSV)
        return {}
    try:
        import pandas as pd
        df = pd.read_csv(R4_BEST_EXIT_CSV)
        index: dict[str, dict[str, Any]] = {}
        for _, row in df.iterrows():
            strategy = row["strategy"]
            index[strategy] = {
                "exit_method": row["exit_method"],
                "total_pnl_pct": float(row["total_pnl_pct"]),
                "n": int(row["n"]),
                "win_rate": float(row["win_rate"]),
            }
        return index
    except Exception as e:
        logger.error("Cannot load R4 best-exit CSV: %s", e)
        return {}


def extract_section_13_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 13 exit_axis_best data for a single strategy.

    Returns dict for Section 13 dossier slot. method='r4_passthrough';
    null cells for 147 strategies not in R4 per honest framing.
    """
    index = _load_r4_best_exit_index()
    row = index.get(strategy)
    if row is None:
        return {
            "best_exit_method": None,
            "best_exit_total_pnl_pct": None,
            "best_exit_n_trades": None,
            "best_exit_win_rate": None,
            "ranking_metric": "total_pnl_pct",
            "in_r4_cube": False,
            "source": "output_batch395_final/exit_strategy_best.csv",
            "method": "r4_passthrough",
            "limitation": (
                "Strategy NOT in R4 cube (post-R4 addition OR insufficient "
                "trades in R4). 147 of 219 strategies have NULL Section 13 "
                "per honest framing. Re-run R4 cube to populate."
            ),
            "stage_5_swap_relevant": False,
        }
    return {
        "best_exit_method": row["exit_method"],
        "best_exit_total_pnl_pct": row["total_pnl_pct"],
        "best_exit_n_trades": row["n"],
        "best_exit_win_rate": row["win_rate"],
        "ranking_metric": "total_pnl_pct",
        "in_r4_cube": True,
        "source": "output_batch395_final/exit_strategy_best.csv",
        "method": "r4_passthrough",
        "limitation": (
            "'Best' ranked by total_pnl_pct (NOT Sharpe per CLAUDE.md "
            "criterion #10). Per-cell Sharpe ranking requires R4 re-run "
            "with per-exit-method metrics; queued as future B-N batch."
        ),
        "stage_5_swap_relevant": True,
    }


def populate_section_13_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 13 exit_axis_best slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_13_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_13_exit_axis_best_26"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
