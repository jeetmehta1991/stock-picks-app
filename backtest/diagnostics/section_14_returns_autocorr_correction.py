# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 14 per CHECKLIST #77.
"""B963 (2026-06-20): Phase P1 batch 23 - Section 14 returns_autocorr_correction.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 14 + Council 67 4/4 verdict
# per owner directive 2026-06-20 'Continue council this. Continue without
# stopping till all sections in P1 are done.' per CHECKLIST #77.

PURPOSE
-------
Section 14 = Lo 2002 autocorrelation correction for Sharpe ratio.
PATH Section 13.3 row 14 spec (canonical):
  'Returns autocorrelation correction (Lo 2002)'
  'Positive autocorr inflates Sharpe; correction applied; corrected-Sharpe
   must re-pass'

Reuses backtest/results/cube_metrics_tier_cde.py::compute_effective_n which
implements the Lo 2002 effective-sample-size formula:
  n_eff = n * (1 - rho1) / (1 + rho1)
Corrected Sharpe = raw_Sharpe * sqrt(n_eff / n).

PRE-BUILD CHECK (Council 67 Executor mandate, executed before coding):
  R4 trade_log.csv: 29,360 trades / 102 firing strategies / cols include
    strategy + regime + pnl_pct. OK
  cube_metrics_tier_cde.compute_effective_n: signature(pnls: np.ndarray)
    returns {autocorr_lag1, effective_n}. OK
  Per-regime computation feasible: trade_log has `regime` column with 4-5
    regime labels including 'crisis_CRISIS_FLAG' annotation per CLAUDE.md.
  CLAUDE.md Sharpe thresholds: overall >= 1.0, per-regime >= 0.7.
  Council 67 First Principles hardening: PER-REGIME AR(1) (not global)
    because regime-stationarity assumption fails on pooled returns.
  Build APPROVED.

METHODOLOGY (per-strategy Lo 2002 correction):
  1. Read R4 trade_log.csv; filter to strategy.
  2. Compute global rho1 + n_eff over all trades.
  3. Compute raw Sharpe + corrected Sharpe = raw_sharpe * sqrt(n_eff / n).
  4. Per regime: compute rho1 + n_eff + raw Sharpe + corrected Sharpe per
     regime bucket (skip regimes with n < 30 -- min_trades floor).
  5. Re-pass flag: corrected_sharpe_overall >= 1.0 (CLAUDE.md threshold).
  6. Per-regime re-pass map: corrected_sharpe >= 0.7 per regime.
  7. Honest framing: if strategy not in R4 trade_log, return not_measured.

OUTPUT SCHEMA per strategy:
{
  "in_r4_trade_log": bool,
  "n_trades_total": int,
  "raw_sharpe_overall": float | None,
  "rho1_overall": float | None,
  "effective_n_overall": int | None,
  "corrected_sharpe_overall": float | None,
  "corrected_sharpe_overall_re_pass": bool | None,  # >= 1.0 threshold
  "per_regime": {
    regime_label: {
      "n_trades": int,
      "raw_sharpe": float,
      "rho1": float,
      "effective_n": int,
      "corrected_sharpe": float,
      "corrected_sharpe_re_pass": bool,  # >= 0.7
    }
  },
  "sharpe_inflation_pct_overall": float | None,
  "method": "lo_2002_effective_n_per_regime",
  "source": "output_batch395_final/trade_log.csv + cube_metrics_tier_cde.compute_effective_n",
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

# CLAUDE.md Sharpe gates
SHARPE_OVERALL_PASS = 1.0
SHARPE_PER_REGIME_PASS = 0.7
# Lo 2002 effective-n requires n>=30; below this rho1 estimate is unreliable
MIN_TRADES_FOR_RHO1 = 30


@lru_cache(maxsize=1)
def _load_r4_trade_log_grouped() -> dict[str, dict[str, list[float]]]:
    """Load R4 trade_log indexed by strategy -> regime -> [pnl_pct list].

    Returns {strategy: {regime: [pnl_pct, ...]}}. Empty if R4 absent.
    """
    if not R4_TRADE_LOG.exists():
        logger.warning("R4 trade_log not found at %s", R4_TRADE_LOG)
        return {}
    try:
        import pandas as pd
        df = pd.read_csv(R4_TRADE_LOG, usecols=["strategy", "regime", "pnl_pct"])
    except Exception as e:
        logger.error("Cannot load R4 trade_log: %s", e)
        return {}
    grouped: dict[str, dict[str, list[float]]] = {}
    for _, row in df.iterrows():
        s = row["strategy"]
        r = row["regime"]
        if not isinstance(s, str) or not isinstance(r, str):
            continue
        try:
            p = float(row["pnl_pct"])
        except (TypeError, ValueError):
            continue
        grouped.setdefault(s, {}).setdefault(r, []).append(p)
    return grouped


def _compute_raw_sharpe(pnls: np.ndarray) -> float:
    """Annualized Sharpe proxy on per-trade pnls; mean / std * sqrt(252)."""
    if pnls is None or len(pnls) < 2:
        return 0.0
    s = pnls.std(ddof=1)
    if s == 0:
        return 0.0
    return float(pnls.mean() / s * np.sqrt(252))


def _compute_lo_2002_correction(pnls_list: list[float]) -> dict[str, Any]:
    """Apply Lo 2002 correction to a returns list.

    Returns dict with raw_sharpe, rho1, effective_n, corrected_sharpe.
    """
    if pnls_list is None or len(pnls_list) < MIN_TRADES_FOR_RHO1:
        return {
            "n_trades": len(pnls_list) if pnls_list else 0,
            "raw_sharpe": None,
            "rho1": None,
            "effective_n": None,
            "corrected_sharpe": None,
        }
    arr = np.asarray(pnls_list, dtype=float)
    n = len(arr)
    raw_sharpe = _compute_raw_sharpe(arr)
    # Reuse cube_metrics_tier_cde.compute_effective_n for canonical Lo 2002 impl
    try:
        from backtest.results.cube_metrics_tier_cde import compute_effective_n
        eff_dict = compute_effective_n(arr)
    except Exception as e:
        logger.error("compute_effective_n failed: %s", e)
        return {
            "n_trades": n,
            "raw_sharpe": round(raw_sharpe, 4),
            "rho1": None,
            "effective_n": None,
            "corrected_sharpe": None,
        }
    rho1 = eff_dict.get("autocorr_lag1")
    eff_n = eff_dict.get("effective_n")
    if eff_n is None or eff_n == 0:
        corrected = None
    else:
        # Lo 2002: corrected Sharpe = raw * sqrt(n_eff / n)
        # (Sharpe magnitude scales with sqrt(sample size) for given mean/std)
        corrected = raw_sharpe * float(np.sqrt(eff_n / n))
    return {
        "n_trades": n,
        "raw_sharpe": round(raw_sharpe, 4),
        "rho1": round(float(rho1), 4) if rho1 is not None else None,
        "effective_n": int(eff_n) if eff_n is not None else None,
        "corrected_sharpe": round(corrected, 4) if corrected is not None else None,
    }


def extract_section_14_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 14 returns_autocorr_correction for a single strategy.

    method='lo_2002_effective_n_per_regime'.
    """
    grouped = _load_r4_trade_log_grouped()
    regime_buckets = grouped.get(strategy)

    if not regime_buckets:
        return {
            "in_r4_trade_log": False,
            "n_trades_total": 0,
            "raw_sharpe_overall": None,
            "rho1_overall": None,
            "effective_n_overall": None,
            "corrected_sharpe_overall": None,
            "corrected_sharpe_overall_re_pass": None,
            "per_regime": {},
            "sharpe_inflation_pct_overall": None,
            "method": "lo_2002_effective_n_per_regime",
            "source": "output_batch395_final/trade_log.csv + cube_metrics_tier_cde.compute_effective_n",
            "limitation": (
                f"Strategy '{strategy}' has no trades in R4 trade_log "
                "(output_batch395_final/trade_log.csv only contains the 102 "
                "strategies that fired in R4). 117 of 219 strategies are NULL "
                "for Section 14 pre-R5 by design. Per Section 9b protocol, "
                "Lo 2002 correction populates from R5 trade_log post-cube launch."
            ),
            "memory_rule_reference": (
                "feedback_pyramid_full_13_tiers_mandatory: corrected-Sharpe is "
                "the honest sample-size-adjusted metric; raw Sharpe inflates "
                "with positive trade-to-trade autocorrelation (positions held "
                "into next day pickup correlated alpha)."
            ),
        }

    # All trades pooled (global rho1)
    all_pnls = [p for pnls in regime_buckets.values() for p in pnls]
    overall = _compute_lo_2002_correction(all_pnls)

    # Per-regime
    per_regime: dict[str, dict[str, Any]] = {}
    for regime, pnls in regime_buckets.items():
        cell = _compute_lo_2002_correction(pnls)
        if cell["corrected_sharpe"] is not None:
            cell["corrected_sharpe_re_pass"] = cell["corrected_sharpe"] >= SHARPE_PER_REGIME_PASS
        else:
            cell["corrected_sharpe_re_pass"] = None
        per_regime[regime] = cell

    # Overall re-pass
    overall_corrected = overall.get("corrected_sharpe")
    overall_re_pass = (
        overall_corrected >= SHARPE_OVERALL_PASS
        if overall_corrected is not None
        else None
    )

    # Sharpe inflation percentage = (raw - corrected) / raw * 100
    inflation_pct: float | None = None
    if overall.get("raw_sharpe") and overall.get("corrected_sharpe") is not None:
        raw = overall["raw_sharpe"]
        if raw != 0:
            inflation_pct = round((raw - overall["corrected_sharpe"]) / raw * 100.0, 2)

    return {
        "in_r4_trade_log": True,
        "n_trades_total": len(all_pnls),
        "raw_sharpe_overall": overall.get("raw_sharpe"),
        "rho1_overall": overall.get("rho1"),
        "effective_n_overall": overall.get("effective_n"),
        "corrected_sharpe_overall": overall.get("corrected_sharpe"),
        "corrected_sharpe_overall_re_pass": overall_re_pass,
        "per_regime": per_regime,
        "sharpe_inflation_pct_overall": inflation_pct,
        "method": "lo_2002_effective_n_per_regime",
        "source": "output_batch395_final/trade_log.csv + cube_metrics_tier_cde.compute_effective_n",
        "limitation": (
            "Lo 2002 AR(1) assumes stationarity within the autocorrelation "
            "window; 7-regime returns are non-stationary across regime breaks. "
            "Per-regime AR(1) computation mitigates by partitioning along the "
            "primary non-stationarity axis (regime classification). Limitations "
            "remaining: (1) within-regime trends may still violate stationarity "
            "if regime classifier is coarse vs true breaks; (2) Sharpe -> "
            "corrected-Sharpe scaling assumes |rho1| < 1 (clipped at 0.99 in "
            "compute_effective_n); (3) regimes with n<30 trades return NULL "
            "per CLAUDE.md min_trades floor (rho1 estimate unreliable below "
            "threshold). Use per_regime corrected_sharpe map as authoritative; "
            "overall corrected_sharpe is convenience aggregation for ranking."
        ),
        "memory_rule_reference": (
            "Council 67 First Principles hardening (B963): per-regime AR(1) "
            "not global AR(1). PATH Section 13.3 row 14 + CLAUDE.md per-regime "
            "verdict (#11). Council 60 honest framing: ship partial when "
            "regime n<30; explicit re-pass flag per cell."
        ),
    }


def populate_section_14_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 14 returns_autocorr_correction slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_14_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_14_returns_autocorr_correction"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
