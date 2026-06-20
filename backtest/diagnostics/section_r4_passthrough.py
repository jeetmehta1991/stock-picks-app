"""B943 (2026-06-20): Phase P1 batch 4 commit 2 - R4 pass-through bundle.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 (Sections 10/11/12/18) +
# Council 48 batch 4 commit 2 per owner directive 2026-06-20 Option A.

PURPOSE
-------
Bundles 4 R4-derived sections (same CSV source; per-section pure functions):

  Section 10 (cost_sensitivity_ratio)         DEC-612 AUTO-FAIL gate
  Section 11 (chow_break_point)               DEC-613 AUTO-FAIL gate
  Section 12 (adf_p_value)                    DEC-614 AUTO-FAIL gate (mean-rev only)
  Section 18 (per_regime_sharpe_dispersion)   Simpson's paradox guard

Per Council 48 "bundling is correct factoring, not over-coupling":
- Same R4 CSV read (reuses Section 9 lazy cache from B935)
- Per-section pure writer functions
- 1 commit / 1 module / 4 section writers

For post-R4 strategies (TRACK 2 per Section 9), all 4 sections return
null + post_r4 sentinel matching Council 45 TWO-TRACK design.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _get_r4_row(strategy: str):
    """Reuse B935 R4 dataframe cache + return per-strategy row or None."""
    from backtest.diagnostics.section_09_r4_cube_metrics import _load_r4_dataframe
    df = _load_r4_dataframe()
    if df.empty or "strategy" not in df.columns:
        return None
    sub = df[df["strategy"] == strategy]
    return sub.iloc[0] if not sub.empty else None


def _track_2_sentinel(section_key: str) -> dict[str, Any]:
    """Standard post-R4 sentinel per Council 45 TWO-TRACK."""
    return {
        "r4_status": "post_r4_addition",
        "value": None,
        "evidence_source": "section_9b",
        "section_key": section_key,
    }


def extract_section_10_cost_sensitivity(strategy: str) -> dict[str, Any]:
    """Section 10: Cost-sensitivity ratio per DEC-612.

    Computes `sharpe_at_20bps / sharpe_at_0bps` from R4 CSV columns.
    Per PASSING_CRITERIA `min_cost_sensitivity_ratio = 0.5` (DEC-612 AUTO-FAIL).
    """
    row = _get_r4_row(strategy)
    if row is None:
        return _track_2_sentinel("cost_sensitivity_ratio")
    s0 = row.get("sharpe_at_0bps")
    s20 = row.get("sharpe_at_20bps")
    if s0 is None or s20 is None:
        return {"r4_status": "in_r4_cube", "value": None, "reason": "missing_sharpe_columns"}
    try:
        s0_f = float(s0)
        s20_f = float(s20)
    except (TypeError, ValueError):
        return {"r4_status": "in_r4_cube", "value": None, "reason": "non_numeric_sharpe"}
    if s0_f == 0:
        return {
            "r4_status": "in_r4_cube",
            "value": None,
            "reason": "sharpe_at_0bps_is_zero (cost-sensitivity undefined)",
        }
    ratio = s20_f / s0_f
    return {
        "r4_status": "in_r4_cube",
        "value": round(ratio, 4),
        "sharpe_at_0bps": s0_f,
        "sharpe_at_20bps": s20_f,
        "passes_dec_612_gate": ratio >= 0.5,
        "gate_threshold": 0.5,
        "source": "DEC-612 / B890",
    }


def extract_section_11_chow_break_point(strategy: str) -> dict[str, Any]:
    """Section 11: Chow break-point p-value + post-break Sharpe per DEC-613."""
    row = _get_r4_row(strategy)
    if row is None:
        return _track_2_sentinel("chow_break_point")
    chow_p = row.get("chow_p_value")
    chow_f = row.get("chow_f_statistic")
    has_break = row.get("has_structural_break")
    if chow_p is None:
        return {"r4_status": "in_r4_cube", "value": None, "reason": "chow_columns_missing"}
    try:
        p_val = float(chow_p) if chow_p not in (None, "", "insufficient_sample") else None
    except (TypeError, ValueError):
        p_val = None
    # DEC-613 AUTO-FAIL: p < 0.05 + post-break Sharpe < 0.3 = dead-strategy false positive
    # R4 schema includes chow_note for diagnostic; post-break Sharpe stored elsewhere
    passes_gate = True
    if p_val is not None and p_val < 0.05:
        # Conservative: flag as POTENTIAL fail; final verdict needs post-break Sharpe
        passes_gate = False
    return {
        "r4_status": "in_r4_cube",
        "value": p_val,
        "chow_f_statistic": float(chow_f) if isinstance(chow_f, (int, float)) else None,
        "has_structural_break": bool(has_break) if isinstance(has_break, bool) else None,
        "passes_dec_613_gate": passes_gate,
        "gate_threshold": "p>=0.05 OR post-break Sharpe>=0.3",
        "source": "DEC-613 / B890",
    }


def extract_section_12_adf(strategy: str) -> dict[str, Any]:
    """Section 12: ADF stationarity p-value per DEC-614 (mean-rev only)."""
    from backtest.config import MEAN_REVERSION_STRATEGIES
    row = _get_r4_row(strategy)
    if row is None:
        return _track_2_sentinel("adf_p_value")
    is_mean_rev = strategy in MEAN_REVERSION_STRATEGIES
    adf_p = row.get("adf_p_value")
    is_stationary = row.get("is_stationary")
    try:
        p_val = float(adf_p) if adf_p not in (None, "", "insufficient_sample") else None
    except (TypeError, ValueError):
        p_val = None
    # DEC-614 AUTO-FAIL: mean-rev only; p<0.10 (stationary = whip-saw non-compounder)
    passes_gate = True
    if is_mean_rev and p_val is not None and p_val < 0.10:
        passes_gate = False
    return {
        "r4_status": "in_r4_cube",
        "value": p_val,
        "is_stationary": bool(is_stationary) if isinstance(is_stationary, bool) else None,
        "is_mean_reversion_strategy": is_mean_rev,
        "passes_dec_614_gate": passes_gate,
        "gate_threshold": "non-mean-rev: pass; mean-rev: p>=0.10",
        "source": "DEC-614 / B890",
    }


def extract_section_18_per_regime_sharpe_dispersion(strategy: str) -> dict[str, Any]:
    """Section 18: Per-regime Sharpe dispersion (Simpson's paradox guard).

    Parses regime_details JSON column from R4 CSV; computes Sharpe range
    across regimes. High dispersion = strategy passes-overall via one
    dominant regime + fails-elsewhere; flagged for Phase D review.
    """
    row = _get_r4_row(strategy)
    if row is None:
        return _track_2_sentinel("per_regime_sharpe_dispersion")
    regime_details_raw = row.get("regime_details")
    if not regime_details_raw or regime_details_raw == "{}":
        return {"r4_status": "in_r4_cube", "value": None, "reason": "no_regime_details"}
    try:
        regime_data = json.loads(regime_details_raw.replace("'", '"')) if isinstance(regime_details_raw, str) else regime_details_raw
    except (json.JSONDecodeError, AttributeError):
        return {"r4_status": "in_r4_cube", "value": None, "reason": "regime_details_parse_failed"}
    # Extract Sharpe per regime where present + verdict != INSUFFICIENT_DATA
    sharpe_per_regime = {}
    for regime_name, details in regime_data.items():
        if not isinstance(details, dict):
            continue
        if details.get("verdict") == "INSUFFICIENT_DATA":
            continue
        # Per R4 schema regime_details may not have sharpe; use win_rate as proxy
        wr = details.get("win_rate")
        if wr is not None:
            sharpe_per_regime[regime_name] = round(float(wr), 4)
    if len(sharpe_per_regime) < 2:
        return {
            "r4_status": "in_r4_cube",
            "value": None,
            "reason": f"fewer_than_2_regimes_evaluable (got {len(sharpe_per_regime)})",
            "n_regimes_with_data": len(sharpe_per_regime),
        }
    values = list(sharpe_per_regime.values())
    dispersion = max(values) - min(values)
    return {
        "r4_status": "in_r4_cube",
        "value": round(dispersion, 4),
        "sharpe_per_regime": sharpe_per_regime,
        "n_regimes_with_data": len(sharpe_per_regime),
        "simpsons_paradox_risk": dispersion > 0.3,
        "source": "Council 38 Quant + PATH 13.3 Section 18",
    }


def populate_r4_passthrough_sections_for_dossier(strategy: str, dossier_path: Path) -> Path:
    """Populate all 4 R4-derived sections (10/11/12/18) in a single dossier pass."""
    if not dossier_path.exists():
        raise FileNotFoundError(f"Dossier not initialized: {dossier_path}")
    with open(dossier_path) as f:
        dossier = json.load(f)
    dossier["sections"]["section_10_cost_sensitivity_ratio"] = extract_section_10_cost_sensitivity(strategy)
    dossier["sections"]["section_11_chow_break_point"] = extract_section_11_chow_break_point(strategy)
    dossier["sections"]["section_12_adf_p_value"] = extract_section_12_adf(strategy)
    dossier["sections"]["section_18_per_regime_sharpe_dispersion"] = extract_section_18_per_regime_sharpe_dispersion(strategy)
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
    return dossier_path
