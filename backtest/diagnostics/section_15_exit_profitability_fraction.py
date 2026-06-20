# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 15 per CHECKLIST #77.
"""B964 (2026-06-20): Phase P1 batch 24 - Section 15 exit_profitability_fraction.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 15 + Council 67 4/4 verdict
# per owner directive 2026-06-20 'Continue council this. Continue without
# stopping till all sections in P1 are done.' per CHECKLIST #77.

PURPOSE
-------
Section 15 = Exit profitability fraction per PATH Section 13.3 row 15:
  'Exit profitability fraction'
  'count(sharpe_exit > 0) / 26 >= 0.4 (>=40% of exits profitable;
   catches 1-of-26 lottery winners)'

Robustness check: a strategy where 1-of-26 exits happens to be profitable
is a lottery-winner, not a robust edge. >=40% profitable exits = the
edge is not pinned to a single exit-rule lucky pick.

PRE-BUILD CHECK (Council 67 Executor mandate, executed before coding):
  R4 trade_log.csv: 29,360 trades / 102 strategies / 19 unique exit_reasons
    (per-strategy avg 3 exit_reasons exercised; max 10).
  exit_strategy_comparison.csv: 25 unique exit_methods aggregate-level.
  exit_strategy_best.csv: 72 strategies x top-1 exit only.
  HONEST LIMITATION: R4 does NOT have full 26-exit cube per-strategy replay.
    Per-strategy per-exit Sharpe must be computed from trade_log directly
    (covers only exits actually triggered for that strategy; cannot evaluate
    counterfactual exits not exercised). Denominator is `exits_measured`
    not `exits_total`. Council 67 First Principles + Council 60 honest
    framing: ship with explicit denominator transparency.
  Council 67 hardening: schema carries exits_measured + exits_total +
    fraction_basis='partial_per_strategy' + WARN_PARTIAL_DENOMINATOR flag.
  Build APPROVED.

METHODOLOGY (per-strategy):
  1. Filter R4 trade_log to strategy.
  2. Group by exit_reason; compute Sharpe-proxy per cell (mean/std * sqrt(252)).
  3. Count cells with sharpe > 0 = `exits_with_positive_sharpe`.
  4. Total cells = `exits_measured` (DIFFERENT from `exits_total`=26).
  5. fraction_positive_per_measured = positive / measured.
  6. fraction_positive_per_total = positive / 26 (canonical PATH denominator).
  7. exit_profitability_check:
       passed if fraction_positive_per_total >= 0.4
       failed if fraction_positive_per_total < 0.4
       not_measured if strategy not in R4 trade_log
  WARN: emit fraction_basis='partial_per_strategy' when measured < 26 and
    flag WARN_PARTIAL_DENOMINATOR=True so consumers don't silently misread.

OUTPUT SCHEMA per strategy:
{
  "in_r4_trade_log": bool,
  "exits_measured": int,                            # exits actually triggered
  "exits_total": int,                               # 26 per PATH canonical
  "exits_with_positive_sharpe": int,
  "fraction_positive_per_measured": float | None,   # winners / measured
  "fraction_positive_per_total": float | None,      # winners / 26
  "per_exit_sharpe": dict[str, float],              # exit_reason -> sharpe_proxy
  "exit_profitability_check": str,                  # passed/failed/not_measured
  "fraction_basis": str,                            # full/partial_per_strategy
  "warn_partial_denominator": bool,
  "method": "trade_log_per_exit_sharpe_proxy",
  "source": "output_batch395_final/trade_log.csv",
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

import numpy as np

logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent.parent
R4_TRADE_LOG = REPO / "output_batch395_final" / "trade_log.csv"

# PATH Section 13.3 row 15 canonical denominator
EXITS_TOTAL = 26
# PATH Section 13.3 row 15 threshold
FRACTION_POSITIVE_FLOOR = 0.4
# Minimum trades to compute Sharpe-proxy reliably
MIN_TRADES_PER_EXIT_CELL = 5


@lru_cache(maxsize=1)
def _load_r4_trade_log_by_strategy_exit() -> dict[str, dict[str, list[float]]]:
    """Load R4 trade_log indexed by strategy -> exit_reason -> [pnl_pct list]."""
    if not R4_TRADE_LOG.exists():
        logger.warning("R4 trade_log not found at %s", R4_TRADE_LOG)
        return {}
    try:
        import pandas as pd
        df = pd.read_csv(R4_TRADE_LOG, usecols=["strategy", "exit_reason", "pnl_pct"])
    except Exception as e:
        logger.error("Cannot load R4 trade_log: %s", e)
        return {}
    grouped: dict[str, dict[str, list[float]]] = {}
    for _, row in df.iterrows():
        s = row["strategy"]
        e = row["exit_reason"]
        if not isinstance(s, str) or not isinstance(e, str):
            continue
        try:
            p = float(row["pnl_pct"])
        except (TypeError, ValueError):
            continue
        grouped.setdefault(s, {}).setdefault(e, []).append(p)
    return grouped


def _sharpe_proxy(pnls: list[float]) -> float | None:
    """Annualized Sharpe proxy on pnls list. None if n < MIN_TRADES_PER_EXIT_CELL."""
    if not pnls or len(pnls) < MIN_TRADES_PER_EXIT_CELL:
        return None
    arr = np.asarray(pnls, dtype=float)
    s = arr.std(ddof=1)
    if s == 0:
        return None
    return float(arr.mean() / s * np.sqrt(252))


def extract_section_15_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 15 exit_profitability_fraction for a single strategy.

    method='trade_log_per_exit_sharpe_proxy'.
    """
    by_exit = _load_r4_trade_log_by_strategy_exit().get(strategy)

    if not by_exit:
        return {
            "in_r4_trade_log": False,
            "exits_measured": 0,
            "exits_total": EXITS_TOTAL,
            "exits_with_positive_sharpe": 0,
            "fraction_positive_per_measured": None,
            "fraction_positive_per_total": None,
            "per_exit_sharpe": {},
            "exit_profitability_check": "not_measured",
            "fraction_basis": "partial_per_strategy",
            "warn_partial_denominator": True,
            "method": "trade_log_per_exit_sharpe_proxy",
            "source": "output_batch395_final/trade_log.csv",
            "limitation": (
                f"Strategy '{strategy}' has no trades in R4 trade_log. "
                "Section 15 is NULL pre-R5 for 117 of 219 strategies by design. "
                "R5 cube will populate per-strategy 26-exit replay completing "
                "the canonical PATH Section 13.3 row 15 denominator."
            ),
            "memory_rule_reference": (
                "Council 60 honest framing (B956 strategic pivot): ship "
                "incomplete data with EXPLICIT denominator transparency. "
                "fraction_basis='partial_per_strategy' + warn_partial_denominator"
                "=True surfaces the limitation to downstream consumers."
            ),
        }

    # Compute Sharpe per (strategy, exit_reason) cell
    per_exit_sharpe: dict[str, float] = {}
    for exit_reason, pnls in by_exit.items():
        sharpe = _sharpe_proxy(pnls)
        if sharpe is not None:
            per_exit_sharpe[exit_reason] = round(sharpe, 4)

    exits_measured = len(per_exit_sharpe)
    exits_with_positive_sharpe = sum(1 for sh in per_exit_sharpe.values() if sh > 0)

    fraction_per_measured: float | None = (
        round(exits_with_positive_sharpe / exits_measured, 4)
        if exits_measured > 0
        else None
    )
    fraction_per_total = round(exits_with_positive_sharpe / EXITS_TOTAL, 4)

    # exit_profitability_check uses canonical PATH denominator (26)
    check: str
    if exits_measured == 0:
        check = "not_measured"
    elif fraction_per_total >= FRACTION_POSITIVE_FLOOR:
        check = "passed"
    else:
        check = "failed"

    fraction_basis = "full" if exits_measured >= EXITS_TOTAL else "partial_per_strategy"
    warn_partial = exits_measured < EXITS_TOTAL

    return {
        "in_r4_trade_log": True,
        "exits_measured": exits_measured,
        "exits_total": EXITS_TOTAL,
        "exits_with_positive_sharpe": exits_with_positive_sharpe,
        "fraction_positive_per_measured": fraction_per_measured,
        "fraction_positive_per_total": fraction_per_total,
        "per_exit_sharpe": per_exit_sharpe,
        "exit_profitability_check": check,
        "fraction_basis": fraction_basis,
        "warn_partial_denominator": warn_partial,
        "method": "trade_log_per_exit_sharpe_proxy",
        "source": "output_batch395_final/trade_log.csv",
        "limitation": (
            "R4 trade_log per-strategy per-exit Sharpe is computed only over "
            "exits actually triggered by the strategy (not full 26-exit cube "
            "replay; that requires R5 batched run). For 102 R4-firing "
            "strategies, average exits_measured=3 of 26; max 10. "
            "fraction_positive_per_total uses canonical PATH denominator (26) "
            "for the >=0.4 threshold gate; fraction_positive_per_measured is "
            "the within-evidence rate for diagnostic use. WARN_PARTIAL_"
            "DENOMINATOR=True when exits_measured<26 indicates the gate "
            "verdict is sample-limited. Per-cell Sharpe requires n>=5 in cell "
            f"(MIN_TRADES_PER_EXIT_CELL); below threshold the cell returns NULL "
            "and is not counted in exits_measured. Resolves to authoritative "
            "fraction at R5 cube launch."
        ),
        "memory_rule_reference": (
            "Council 67 Executor hardening (B964): exits_measured/exits_total "
            "explicit + WARN_PARTIAL_DENOMINATOR flag. PATH Section 13.3 row 15 "
            "+ Council 60 honest framing. feedback_pyramid_full_13_tiers_"
            "mandatory: partial gate must be reported as partial."
        ),
    }


def populate_section_15_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 15 exit_profitability_fraction slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_15_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_15_exit_profitability_fraction"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
