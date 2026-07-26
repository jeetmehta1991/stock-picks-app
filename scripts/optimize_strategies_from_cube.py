"""Batch 388: per-strategy optimization candidate generator.

Source (per CHECKLIST #77): owner directive 2026-05-26 - methodology for
"how do we optimize each strategy". This script implements the structured
optimization pipeline (Stages 2-3) so each strategy emerges with
empirical-evidence-based candidates rather than ad-hoc edits.

Per memory directive `project_no_apriori_strategy_pruning.md` + the
cube-eval principle (Batches 377-386), this script ONLY proposes
candidates - it does NOT apply changes. Owner reviews the per-strategy
JSON output + summary, approves each candidate explicitly, and I
implement approved changes in separate batches.

== INPUTS ==
  --input-dir <output_phase_1a_beta_*>/
    trade_log.csv             (per-trade fires with signals_at_entry)
    trade_exit_detail.csv     (cube replay, 25 exits x per-fire)
    verdict_cube.csv          (DEC-426 5-Gate verdict per cell)
    skipped_trades.csv        (gate rejection reasons)

== OUTPUTS ==
  --output-dir <output_dir>/
    optimization_candidates_<strategy>.json   per strategy
    optimization_summary.md                    living doc; owner reviews

== DIMENSIONS A-I ==
  A. Entry-gate thresholds  (BINDING vs LOOSE clauses per Batch 380 pattern)
  B. Compound logic         (AND-clause individual fire rates + correlations)
  C. Regime applicability   (per-regime DEC-426 5-Gate verdict)
  D. Exit method pairing    (best exit by Sharpe per strategy)
  E. Position sizing tier   (Sharpe -> tier mapping recommendation)
  F. Universe filtering     (per-sector / cap_band verdict)
  G. Hold duration limits   (empirical hold-days distribution)
  H. Cooldown / re-entry    (post-stop re-entry behavior)
  I. Macro overlay          (per-macro-regime verdict if available)

== USAGE ==
  python scripts/optimize_strategies_from_cube.py \\
      --input-dir output_phase_1a_beta_single_local \\
      --output-dir output_optimization_candidates
  python scripts/optimize_strategies_from_cube.py --strategy buyback_8k_recent_long
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------
# DEC-426 5-Gate thresholds (from config.py canonical)
# ---------------------------------------------------------------------
try:
    from backtest.config import DEC_422_FIVE_GATE_VALIDITY
    GATE_N_MIN = DEC_422_FIVE_GATE_VALIDITY["min_trades_per_cell"]
    GATE_P_MAX = DEC_422_FIVE_GATE_VALIDITY["max_p_value"]
    GATE_PSR_MIN = DEC_422_FIVE_GATE_VALIDITY["min_psr"]
    GATE_T_MIN = DEC_422_FIVE_GATE_VALIDITY["min_t_stat"]
    GATE_RR_MIN = DEC_422_FIVE_GATE_VALIDITY["min_rr"]
except Exception:
    GATE_N_MIN, GATE_P_MAX, GATE_PSR_MIN, GATE_T_MIN, GATE_RR_MIN = 30, 0.05, 0.95, 3.4, 2.0

# DEC-021 tier sizing (from CLAUDE.md approved table)
TIER_SIZE_PCT = {
    "EXCEPTIONAL": 5.0, "VERY_HIGH": 4.0, "HIGH": 3.0,
    "MEDIUM_HIGH": 1.5, "MEDIUM": 0.75, "LOW": 0.0,
}


# ---------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------
def _cell_stats(pnls: pd.Series, hold_days: pd.Series | None = None) -> dict:
    """Per-cell stats with Batch 375 trade-frequency Sharpe annualization.

    Batch 457 (2026-05-29): adds skew + kurtosis so _dec426_verdict can
    call metrics.py::_deflated_sharpe instead of hardcoding PSR=False.
    Closes queue items AU1 + #4 (PSR-hardcoded-False P0).
    """
    pnls = pnls.astype(float)
    n = len(pnls)
    if n == 0:
        return {"n": 0}
    wins = pnls[pnls > 0]
    losses = pnls[pnls <= 0]
    wr = float(wins.shape[0]) / n
    mu = float(pnls.mean())
    std = float(pnls.std(ddof=1)) if n > 1 else 0.0
    gw = float(wins.sum()) if len(wins) > 0 else 0.0
    gl = float(abs(losses.sum())) if len(losses) > 0 else 0.0
    pf = gw / gl if gl > 0 else (99.0 if gw > 0 else 0.0)
    # Trade-frequency Sharpe (Batch 375 DEC-246 fix)
    if hold_days is not None and len(hold_days) > 0:
        avg_hold = float(hold_days.mean())
        n_tpy = 252.0 / max(avg_hold, 1.0)
        sharpe = (mu / std * np.sqrt(n_tpy)) if std > 0 else 0.0
    else:
        sharpe = (mu / std * np.sqrt(252)) if std > 0 else 0.0
    t_stat = (mu * np.sqrt(n)) / std if std > 0 else 0.0
    # Batch 457: skew + kurtosis for PSR computation downstream.
    if n >= 4 and std > 0:
        skew_val = float(pnls.skew())
        kurt_val = float(pnls.kurt())  # pandas .kurt() returns excess kurtosis
    else:
        skew_val = 0.0
        kurt_val = 0.0
    # Batch 502 (2026-05-31, 0a path 1): emit ACTUAL R:R alongside
    # profit_factor. R:R = avg_win / abs(avg_loss); profit_factor =
    # (WR/(1-WR)) * R:R. The current 5-Gate uses profit_factor under
    # the "rr_>=_2.0" key which is mis-named (see queue row 0a +
    # test_batch492_0a counter-example: WR=60% PF=2.0 implies R:R=1.33,
    # NOT 2.0). Path-1 fix: ship actual R:R alongside so gate-key
    # rename in _dec426_verdict is honest + a future Path-2 swap can
    # gate on the ACTUAL R:R without recomputing.
    avg_win  = float(wins.mean()) if len(wins) > 0 else 0.0
    avg_loss_abs = float(abs(losses.mean())) if len(losses) > 0 else 0.0
    rr_actual = (avg_win / avg_loss_abs) if avg_loss_abs > 0 else (
        99.0 if avg_win > 0 else 0.0
    )
    return {
        "n":           n,
        "win_rate":    round(wr, 4),
        "mean_pp":     round(mu, 4),
        "std_pp":      round(std, 4),
        "sum_pp":      round(float(pnls.sum()), 4),
        "profit_factor": round(pf, 4),
        # Batch 502 (0a path 1): true R:R = avg_win / abs(avg_loss).
        "rr_ratio":    round(rr_actual, 4),
        "sharpe":      round(sharpe, 4),
        "t_stat":      round(t_stat, 4),
        "skew":        round(skew_val, 4),
        "kurtosis":    round(kurt_val, 4),
    }


def _dec426_verdict(stats: dict, m_total_candidates: int = 1) -> dict:
    """Apply DEC-426 5-Gate + Bonferroni correction."""
    n = stats.get("n", 0)
    if n < GATE_N_MIN:
        return {"verdict": "INSUFFICIENT_SAMPLE", "five_gate_pass": False,
                "gates": {"n_>=_30": False}}
    from scipy.stats import t as t_dist
    raw_p = float(2 * (1 - t_dist.cdf(abs(stats["t_stat"]),
                                       df=max(1, n - 1)))) if stats["std_pp"] > 0 else 1.0
    bonf_p = min(1.0, raw_p * m_total_candidates)
    # Batch 457 (2026-05-29): replace placeholder PSR=False with real
    # deflated-Sharpe PSR via metrics.py::_deflated_sharpe. Closes
    # queue items AU1 + #4 (PSR-hardcoded-False P0).
    # Requires _cell_stats to have populated skew + kurtosis (Batch 457).
    from backtest.results.metrics import _deflated_sharpe
    psr_result = _deflated_sharpe(
        sharpe=stats.get("sharpe", 0.0),
        n_trades=n,
        skew=stats.get("skew", 0.0),
        kurtosis=stats.get("kurtosis", 3.0),
    )
    psr_value = psr_result.get("psr")
    psr_pass = (psr_value is not None) and (psr_value >= GATE_PSR_MIN)
    # Batch 502 (Path 1): renamed "rr_>=_2.0" -> "pf_>=_2.0" + shipped
    # informational "rr_actual_>=_2.0".
    # Batch 506 (2026-05-31, owner decision Path 2): SWAP the enforced
    # gate from profit_factor to actual R:R. Per Batch 492 counter-
    # examples (WR=60% PF=2.0 implies R:R=1.33; 90% WR + R:R=0.5 has
    # PF=4.5), the previously-enforced PF gate let cells through that
    # the dict-key name "rr_>=_2.0" would have rejected. The enforced
    # gate is now actual R:R = avg_win / abs(avg_loss). The pf reading
    # stays in the gates dict as informational (NOT enforced).
    rr_actual_pass = stats.get("rr_ratio", 0.0) >= GATE_RR_MIN
    pf_pass = stats["profit_factor"] >= GATE_RR_MIN
    gates = {
        "n_>=_30":          n >= GATE_N_MIN,
        "p_<_0.05":         bonf_p < GATE_P_MAX,
        "psr_>=_0.95":      psr_pass,
        "t_>=_3.4":         stats["t_stat"] >= GATE_T_MIN,
        # Batch 506: rr_actual_>=_2.0 is NOW the enforced gate.
        "rr_actual_>=_2.0": rr_actual_pass,
        # Batch 506: pf_>=_2.0 stays informational (NOT enforced); kept
        # for backward-compat dashboards + diagnostic comparison.
        "pf_>=_2.0":        pf_pass,
    }
    enforced_gates = ["n_>=_30", "p_<_0.05", "t_>=_3.4", "rr_actual_>=_2.0"]
    return {
        "verdict":         "PASS" if all(gates[k] for k in enforced_gates) else "FAIL",
        "five_gate_pass":  all(gates[k] for k in enforced_gates + ["psr_>=_0.95"]),
        "gates":           gates,
        "raw_p":           round(raw_p, 6),
        "bonferroni_p":    round(bonf_p, 6),
        "psr":             round(psr_value, 4) if psr_value is not None else None,
        "deflated_sharpe": round(psr_result.get("deflated_sharpe"), 4) if psr_result.get("deflated_sharpe") is not None else None,
    }


# ---------------------------------------------------------------------
# Dimension A: entry-gate thresholds (BINDING vs LOOSE per Batch 380)
# ---------------------------------------------------------------------
def _analyze_thresholds(strategy: str, sub_tl: pd.DataFrame,
                         screener_source: str) -> dict:
    """Dim A: extract numeric thresholds from screener.py source + measure
    empirical distance at fires."""
    m = re.search(rf'def strat_{re.escape(strategy)}\(s\):(.+?)(?=\ndef strat_|\nALL_STRATEGIES|\Z)',
                  screener_source, re.DOTALL)
    if not m:
        return {"status": "function_not_found"}
    body = m.group(1)
    thresholds = re.findall(
        r's\.get\(["\']([a-z_][a-z_0-9]*)["\']\s*,[^)]+\)\s*([<>=!]{1,2})\s*([0-9.]+)',
        body,
    )
    sig_dicts = []
    for s in sub_tl["signals_at_entry"]:
        try:
            sig_dicts.append(json.loads(s) if isinstance(s, str) else {})
        except Exception:
            continue
    candidates = []
    for k, op, thresh_str in thresholds:
        thresh = float(thresh_str)
        vals = [d.get(k) for d in sig_dicts if k in d]
        numeric = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if not numeric:
            continue
        arr = np.array(numeric, dtype=float)
        s_min, s_p25, s_med, s_p75, s_max = (
            float(arr.min()), float(np.percentile(arr, 25)),
            float(np.median(arr)), float(np.percentile(arr, 75)),
            float(arr.max()),
        )
        binding = False
        loose = False
        if op in (">", ">="):
            margin_min = s_min - thresh  # how much min exceeds threshold
            binding = abs(margin_min) < 0.1 * max(abs(thresh), 0.01)
            loose = margin_min > 0.5 * max(abs(thresh), 0.01)
        elif op in ("<", "<="):
            margin_max = thresh - s_max
            binding = abs(margin_max) < 0.1 * max(abs(thresh), 0.01)
            loose = margin_max > 0.5 * max(abs(thresh), 0.01)
        # Candidate loosen (BINDING -> propose ~25% wider)
        proposal = None
        if binding:
            if op in (">", ">="):
                new_thresh = round(thresh * 0.75, 3) if thresh != 0 else thresh - 0.25
                proposal = f"loosen {k} {op} {thresh} -> {new_thresh} (BINDING; min fire={s_min:.3f})"
            elif op in ("<", "<="):
                new_thresh = round(thresh * 1.25, 3) if thresh != 0 else thresh + 0.25
                proposal = f"loosen {k} {op} {thresh} -> {new_thresh} (BINDING; max fire={s_max:.3f})"
        elif loose:
            if op in (">", ">="):
                proposal = f"tighten {k} {op} {thresh} -> ~{round(s_p25, 3)} (LOOSE; p25 fire={s_p25:.3f})"
            elif op in ("<", "<="):
                proposal = f"tighten {k} {op} {thresh} -> ~{round(s_p75, 3)} (LOOSE; p75 fire={s_p75:.3f})"
        candidates.append({
            "clause":       f"{k} {op} {thresh}",
            "empirical":    {"min": round(s_min, 4), "p25": round(s_p25, 4),
                             "median": round(s_med, 4),
                             "p75": round(s_p75, 4), "max": round(s_max, 4),
                             "n": len(numeric)},
            "verdict":      "BINDING" if binding else "LOOSE" if loose else "normal",
            "proposal":     proposal,
        })
    return {"status": "ok", "candidates": candidates}


# ---------------------------------------------------------------------
# Dimension B: compound logic (per-clause fire rate from signals)
# ---------------------------------------------------------------------
def _analyze_compound(strategy: str, sub_tl: pd.DataFrame,
                       screener_source: str) -> dict:
    """Dim B: per-clause individual fire rate. If a clause fires 90%+ on
    fired trades, it's not selective. If it fires <30%, it's restrictive."""
    m = re.search(rf'def strat_{re.escape(strategy)}\(s\):(.+?)(?=\ndef strat_|\nALL_STRATEGIES|\Z)',
                  screener_source, re.DOTALL)
    if not m:
        return {"status": "function_not_found"}
    body = m.group(1)
    keys = sorted(set(re.findall(r's\.get\(["\']([a-z_][a-z_0-9]*)', body)))
    sig_dicts = []
    for s in sub_tl["signals_at_entry"]:
        try:
            sig_dicts.append(json.loads(s) if isinstance(s, str) else {})
        except Exception:
            continue
    per_clause = []
    for k in keys:
        vals = [d.get(k) for d in sig_dicts if k in d]
        if not vals:
            continue
        # Boolean clause fire rate
        if all(isinstance(v, bool) for v in vals):
            n_true = sum(1 for v in vals if v)
            rate = n_true / len(vals) * 100
        else:
            rate = 100.0  # numeric clause - presence-only
        per_clause.append({"clause": k, "fires_at": round(rate, 1),
                           "n_present": len(vals)})
    # Identify restrictive (low fire rate) vs always-on (high) clauses
    restrictive = [c for c in per_clause if c["fires_at"] < 30]
    always_on = [c for c in per_clause if c["fires_at"] > 90]
    proposals = []
    if restrictive:
        for c in restrictive:
            proposals.append(
                f"consider OR-fallback for `{c['clause']}` (fires only {c['fires_at']}% on fired trades)")
    if always_on and len(per_clause) > 1:
        proposals.append(
            f"clauses {[c['clause'] for c in always_on]} fire 90%+ - "
            f"removing them wouldn't reduce admission significantly")
    return {
        "status":      "ok",
        "per_clause":  per_clause,
        "restrictive": restrictive,
        "always_on":   always_on,
        "proposals":   proposals,
    }


# ---------------------------------------------------------------------
# Dimension C: per-regime verdict
# ---------------------------------------------------------------------
def _analyze_regime(strategy: str, sub_tl: pd.DataFrame,
                     m_total_candidates: int) -> dict:
    out = {}
    for regime in sorted(sub_tl["regime"].unique()):
        regime_sub = sub_tl[sub_tl["regime"] == regime]
        hd = regime_sub["hold_days"] if "hold_days" in regime_sub.columns else None
        st = _cell_stats(regime_sub["pnl_pct"], hd)
        v = _dec426_verdict(st, m_total_candidates=m_total_candidates)
        out[regime] = {**st, **v}
    proposals = []
    pass_regimes = [r for r, d in out.items() if d.get("verdict") == "PASS"]
    fail_regimes = [r for r, d in out.items() if d.get("verdict") == "FAIL"]
    if pass_regimes and fail_regimes:
        proposals.append(
            f"set STRATEGY_REGIME_AFFINITY[{strategy}] = {{{', '.join(pass_regimes)}}} "
            f"(PASS verdicts only; FAIL in {fail_regimes})")
    return {"status": "ok", "per_regime": out, "proposals": proposals}


# ---------------------------------------------------------------------
# Dimension D: best exit method (from cube)
# ---------------------------------------------------------------------
def _analyze_exit(strategy: str, sub_cube: pd.DataFrame,
                   m_total_candidates: int) -> dict:
    if sub_cube.empty:
        return {"status": "no_cube_data"}
    rows = []
    for em in sub_cube["exit_method"].unique():
        cell = sub_cube[sub_cube["exit_method"] == em]
        hd = cell["hold_days"] if "hold_days" in cell.columns else None
        st = _cell_stats(cell["pnl_pct"], hd)
        v = _dec426_verdict(st, m_total_candidates=m_total_candidates)
        rows.append({"exit_method": em, **st, **v})
    rows.sort(key=lambda r: -r.get("sharpe", -999))
    proposals = []
    if rows and rows[0].get("five_gate_pass"):
        proposals.append(
            f"STRATEGY_EXIT_OVERRIDE[{strategy}] = {{'exit_method': '{rows[0]['exit_method']}'}} "
            f"(n={rows[0]['n']}, sharpe={rows[0]['sharpe']}, 5-gate-pass)")
    elif rows:
        proposals.append(
            f"best exit `{rows[0]['exit_method']}` has Sharpe {rows[0]['sharpe']} "
            f"(n={rows[0]['n']}); 5-gate {rows[0].get('verdict', 'INSUFFICIENT')}")
    return {"status": "ok", "ranked": rows[:10], "proposals": proposals}


# ---------------------------------------------------------------------
# Dimension E: sizing tier recommendation
# ---------------------------------------------------------------------
def _analyze_sizing(strategy: str, agg_stats: dict) -> dict:
    sharpe = agg_stats.get("sharpe", 0)
    if sharpe >= 2.0:
        tier_rec = "EXCEPTIONAL"
    elif sharpe >= 1.5:
        tier_rec = "VERY_HIGH"
    elif sharpe >= 1.0:
        tier_rec = "HIGH"
    elif sharpe >= 0.7:
        tier_rec = "MEDIUM_HIGH"
    elif sharpe >= 0.4:
        tier_rec = "MEDIUM"
    else:
        tier_rec = "LOW (skip)"
    return {
        "status":       "ok",
        "agg_sharpe":   sharpe,
        "tier_rec":     tier_rec,
        "size_pct":     TIER_SIZE_PCT.get(tier_rec.split()[0], 0.0),
    }


# ---------------------------------------------------------------------
# Dimension F: per-sector / cap-band verdict
# ---------------------------------------------------------------------
def _analyze_universe(strategy: str, sub_tl: pd.DataFrame,
                       m_total_candidates: int) -> dict:
    if "sector" not in sub_tl.columns:
        return {"status": "no_sector_data"}
    per_sector = {}
    for sec in sorted(sub_tl["sector"].dropna().unique()):
        sec_sub = sub_tl[sub_tl["sector"] == sec]
        if len(sec_sub) < 5:
            continue
        hd = sec_sub["hold_days"] if "hold_days" in sec_sub.columns else None
        st = _cell_stats(sec_sub["pnl_pct"], hd)
        v = _dec426_verdict(st, m_total_candidates=m_total_candidates)
        per_sector[sec] = {**st, **v}
    pass_sectors = [s for s, d in per_sector.items() if d.get("verdict") == "PASS"]
    fail_sectors = [s for s, d in per_sector.items() if d.get("verdict") == "FAIL" and d["n"] >= GATE_N_MIN]
    proposals = []
    if pass_sectors and fail_sectors:
        proposals.append(
            f"filter universe: allow only sectors {pass_sectors} for {strategy}; "
            f"FAIL n>=30 sectors: {fail_sectors}")
    return {"status": "ok", "per_sector": per_sector, "proposals": proposals}


# ---------------------------------------------------------------------
# Dimension G: hold-duration distribution
# ---------------------------------------------------------------------
def _analyze_hold_duration(strategy: str, sub_tl: pd.DataFrame) -> dict:
    if "hold_days" not in sub_tl.columns or sub_tl.empty:
        return {"status": "no_hold_data"}
    hd = sub_tl["hold_days"].dropna().astype(float)
    if len(hd) < 5:
        return {"status": "insufficient_n"}
    stats = {
        "n":      len(hd),
        "min":    int(hd.min()),
        "p25":    round(float(np.percentile(hd, 25)), 1),
        "median": round(float(np.median(hd)), 1),
        "p75":    round(float(np.percentile(hd, 75)), 1),
        "max":    int(hd.max()),
    }
    proposals = []
    if stats["p75"] <= 5:
        proposals.append(f"consider time_stop_5d exit (75% of fires close by day 5)")
    elif stats["p75"] <= 10:
        proposals.append(f"consider time_stop_10d exit (75% close by day 10)")
    elif stats["p75"] <= 20:
        proposals.append(f"consider time_stop_20d exit (75% close by day 20)")
    return {"status": "ok", "distribution": stats, "proposals": proposals}


# ---------------------------------------------------------------------
# Dimension H: cooldown / re-entry behavior
# ---------------------------------------------------------------------
def _analyze_cooldown(strategy: str, sub_tl: pd.DataFrame) -> dict:
    if "ticker" not in sub_tl.columns or sub_tl.empty:
        return {"status": "no_ticker_data"}
    sub_tl = sub_tl.copy()
    sub_tl["entry_dt"] = pd.to_datetime(sub_tl["entry_date"], errors="coerce")
    reentries_within_5d = 0
    for tkr in sub_tl["ticker"].unique():
        tkr_fires = sub_tl[sub_tl["ticker"] == tkr].sort_values("entry_dt")
        if len(tkr_fires) < 2:
            continue
        gaps = tkr_fires["entry_dt"].diff().dt.days
        reentries_within_5d += (gaps <= 5).sum()
    proposals = []
    if reentries_within_5d > 0.1 * len(sub_tl):
        proposals.append(
            f"{reentries_within_5d} same-ticker re-entries within 5 days "
            f"({reentries_within_5d / len(sub_tl) * 100:.1f}% of fires) - "
            f"consider per-strategy cooldown override")
    return {"status": "ok", "reentries_within_5d": int(reentries_within_5d),
            "proposals": proposals}


# ---------------------------------------------------------------------
# Dimension I: macro overlay (per-VIX-band / per-yield-curve verdict)
# ---------------------------------------------------------------------
def _analyze_macro(strategy: str, sub_tl: pd.DataFrame,
                    m_total_candidates: int) -> dict:
    sig_dicts = []
    for s in sub_tl["signals_at_entry"]:
        try:
            sig_dicts.append(json.loads(s) if isinstance(s, str) else {})
        except Exception:
            sig_dicts.append({})
    if not sig_dicts or len(sig_dicts) != len(sub_tl):
        return {"status": "no_macro_data"}
    sub_tl = sub_tl.copy().reset_index(drop=True)
    sub_tl["vix_band"] = ["high" if d.get("vix_value", 0) > 25 else
                          ("normal" if d.get("vix_value", 0) >= 15 else "low")
                          for d in sig_dicts]
    per_vix = {}
    for vb in sub_tl["vix_band"].unique():
        sub = sub_tl[sub_tl["vix_band"] == vb]
        if len(sub) < GATE_N_MIN:
            continue
        hd = sub["hold_days"] if "hold_days" in sub.columns else None
        st = _cell_stats(sub["pnl_pct"], hd)
        v = _dec426_verdict(st, m_total_candidates=m_total_candidates)
        per_vix[vb] = {**st, **v}
    proposals = []
    pass_bands = [b for b, d in per_vix.items() if d.get("verdict") == "PASS"]
    fail_bands = [b for b, d in per_vix.items() if d.get("verdict") == "FAIL"]
    if pass_bands and fail_bands:
        proposals.append(
            f"macro overlay: {strategy} PASSes in VIX={pass_bands}; FAILs in {fail_bands}")
    return {"status": "ok", "per_vix_band": per_vix, "proposals": proposals}


# ---------------------------------------------------------------------
# Top-level orchestrator
# ---------------------------------------------------------------------
def optimize_strategy(strategy: str, trade_log: pd.DataFrame,
                       cube: pd.DataFrame, screener_source: str,
                       m_total_candidates: int) -> dict:
    sub_tl = trade_log[trade_log["strategy"] == strategy].copy()
    sub_cube = cube[cube["strategy"] == strategy].copy() if not cube.empty else pd.DataFrame()
    if sub_tl.empty:
        return {"strategy": strategy, "status": "no_fires",
                "n_trades": 0}
    # Aggregate stats
    hd = sub_tl["hold_days"] if "hold_days" in sub_tl.columns else None
    agg = _cell_stats(sub_tl["pnl_pct"], hd)
    verdict = _dec426_verdict(agg, m_total_candidates=m_total_candidates)
    return {
        "strategy":           strategy,
        "n_trades":           int(len(sub_tl)),
        "aggregate":          {**agg, **verdict},
        "dimension_a_thresholds":  _analyze_thresholds(strategy, sub_tl, screener_source),
        "dimension_b_compound":    _analyze_compound(strategy, sub_tl, screener_source),
        "dimension_c_regime":      _analyze_regime(strategy, sub_tl, m_total_candidates),
        "dimension_d_exit":        _analyze_exit(strategy, sub_cube, m_total_candidates),
        "dimension_e_sizing":      _analyze_sizing(strategy, agg),
        "dimension_f_universe":    _analyze_universe(strategy, sub_tl, m_total_candidates),
        "dimension_g_hold":        _analyze_hold_duration(strategy, sub_tl),
        "dimension_h_cooldown":    _analyze_cooldown(strategy, sub_tl),
        "dimension_i_macro":       _analyze_macro(strategy, sub_tl, m_total_candidates),
    }


def producer_zero_reaudit(trade_log: pd.DataFrame,
                           skipped: pd.DataFrame,
                           screener_source: str) -> dict:
    """Batch 389 post-cube re-audit: re-classify quiet strategies into
    PRODUCER_LAYER_ZERO vs COMPOUND_RESTRICTIVE vs SKIPPED_AT_ENGINE.

    Stage D pilot showed 9 of 49 prior "PRODUCER_LAYER_ZERO" classifications
    were FALSE POSITIVES - strategies that DID produce candidates but
    were filtered downstream. With Batches 377/383/384/386 removing all
    downstream gates, this re-audit produces the TRUE producer-zero set.

    Classification (3 buckets):
      PRODUCER_LAYER_ZERO_LIKELY  - quiet AND none of its gate keys ever
                                    emit values in fired-trade signals
      COMPOUND_RESTRICTIVE        - quiet AND individual clauses emit but
                                    the AND-compound never satisfies
      SKIPPED_AT_ENGINE           - quiet AND appears in skipped_trades
                                    (false-positive PRODUCER_LAYER_ZERO; gate
                                    removal SHOULD fix; if still quiet
                                    post-cube, there's a different gate)
    """
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.config import (DEPRECATED_STRATEGIES,
                                   STRATEGIES_DISABLED_MISSING_PRODUCER)
    all_active = set(ALL_STRATEGIES.keys()) - DEPRECATED_STRATEGIES - STRATEGIES_DISABLED_MISSING_PRODUCER
    fired_set = set(trade_log["strategy"].unique())
    quiet = sorted(all_active - fired_set)
    skipped_set = set(skipped["strategy"].unique()) if not skipped.empty else set()

    # Build empirical signal corpus from fired trades to check key emit rates
    sig_dicts = []
    for s in trade_log["signals_at_entry"]:
        try:
            sig_dicts.append(json.loads(s) if isinstance(s, str) else {})
        except Exception:
            continue

    def _key_present_anywhere(key: str) -> bool:
        return any(key in d for d in sig_dicts)

    def _key_emits_truthy(key: str) -> bool:
        n_present = 0
        n_truthy = 0
        for d in sig_dicts:
            if key in d:
                n_present += 1
                v = d[key]
                if isinstance(v, bool):
                    if v:
                        n_truthy += 1
                elif isinstance(v, (int, float)):
                    if v != 0:
                        n_truthy += 1
                elif isinstance(v, str):
                    if v and v not in ("unknown", "None"):
                        n_truthy += 1
        return n_truthy > 0 if n_present > 0 else False

    buckets = {
        "PRODUCER_LAYER_ZERO_LIKELY": [],
        "COMPOUND_RESTRICTIVE":       [],
        "SKIPPED_AT_ENGINE":          [],
    }
    per_strategy = {}
    for strat in quiet:
        m = re.search(rf'def strat_{re.escape(strat)}\(s\):(.+?)(?=\ndef strat_|\nALL_STRATEGIES|\Z)',
                      screener_source, re.DOTALL)
        if not m:
            per_strategy[strat] = {"bucket": "FUNCTION_NOT_FOUND", "gate_keys": []}
            continue
        body = m.group(1)
        gate_keys = sorted(set(re.findall(r's\.get\(["\']([a-z_][a-z_0-9]*)', body)))
        n_present = sum(1 for k in gate_keys if _key_present_anywhere(k))
        n_truthy = sum(1 for k in gate_keys if _key_emits_truthy(k))

        if strat in skipped_set:
            bucket = "SKIPPED_AT_ENGINE"
        elif n_truthy == 0 and len(gate_keys) > 0:
            bucket = "PRODUCER_LAYER_ZERO_LIKELY"
        else:
            bucket = "COMPOUND_RESTRICTIVE"
        buckets[bucket].append(strat)
        per_strategy[strat] = {
            "bucket":         bucket,
            "n_gate_keys":    len(gate_keys),
            "n_keys_present": n_present,
            "n_keys_truthy":  n_truthy,
            "gate_keys":      gate_keys[:10],
            "dominant_skip_reason": (
                skipped[skipped["strategy"] == strat]["reason"].mode().iloc[0]
                if strat in skipped_set and not skipped[skipped["strategy"] == strat].empty
                else None
            ),
        }

    # Family clustering of PRODUCER_LAYER_ZERO_LIKELY by shared missing key
    family_clusters = defaultdict(list)
    for strat in buckets["PRODUCER_LAYER_ZERO_LIKELY"]:
        keys = per_strategy[strat]["gate_keys"]
        # First non-truthy key = likely the binding-missing producer
        for k in keys:
            if not _key_emits_truthy(k):
                family_clusters[k].append(strat)
                break

    # Identify priority families (n>=3 affected)
    priority_families = {k: v for k, v in family_clusters.items() if len(v) >= 3}

    return {
        "summary": {
            "active_count":                   len(all_active),
            "fired_count":                    len(fired_set & all_active),
            "quiet_count":                    len(quiet),
            "PRODUCER_LAYER_ZERO_LIKELY":     len(buckets["PRODUCER_LAYER_ZERO_LIKELY"]),
            "COMPOUND_RESTRICTIVE":           len(buckets["COMPOUND_RESTRICTIVE"]),
            "SKIPPED_AT_ENGINE":              len(buckets["SKIPPED_AT_ENGINE"]),
        },
        "buckets":             {k: sorted(v) for k, v in buckets.items()},
        "per_strategy":        per_strategy,
        "family_clusters":     {k: sorted(v) for k, v in family_clusters.items()},
        "priority_families":   {k: sorted(v) for k, v in priority_families.items()},
    }


def analyze_exit_methods(cube: pd.DataFrame, m_total_candidates: int) -> dict:
    """Batch 391: per-(strategy x exit) cell analysis + cross-strategy
    exit-method ranking. Owner directive 2026-05-26: similar to strategy
    optimization, we need to optimize exits too, especially at a
    strategyxexit combination level.

    Three layers of analysis:

    Layer 1 - per-exit-method aggregate (across all paired strategies):
      for each exit_method in EXIT_STRATEGIES, compute aggregate Sharpe /
      PF / WR / total n across all strategies that used it; rank
      exit methods by aggregate performance

    Layer 2 - per-(strategy x exit_method) cell verdict:
      for each cell with n >= 5, compute Sharpe + DEC-426 5-Gate;
      flag cells where the exit is the cell-winner vs cell-loser

    Layer 3 - parameter-variant ranking (within an exit family):
      time_stop_10d vs time_stop_20d (vs class_time_stop)
      r_multiple_2r vs r_multiple_3r
      trailing_5pct vs trailing_10pct vs trailing_15pct
      For each strategy with cells in multiple variants of a family,
      identify the variant winner.
    """
    if cube is None or cube.empty:
        return {"status": "no_cube_data"}

    # Layer 1: per-exit-method aggregate
    layer_1 = {}
    for em in sorted(cube["exit_method"].unique()):
        cell = cube[cube["exit_method"] == em]
        hd = cell["hold_days"] if "hold_days" in cell.columns else None
        st = _cell_stats(cell["pnl_pct"], hd)
        v = _dec426_verdict(st, m_total_candidates=m_total_candidates)
        n_strats_paired = int(cell["strategy"].nunique())
        layer_1[em] = {
            **st, **v,
            "n_strategies_paired": n_strats_paired,
        }

    # Layer 2: per-(strategy x exit) cell
    layer_2 = []
    for (strat, em), cell in cube.groupby(["strategy", "exit_method"]):
        if len(cell) < 5:
            continue
        hd = cell["hold_days"] if "hold_days" in cell.columns else None
        st = _cell_stats(cell["pnl_pct"], hd)
        v = _dec426_verdict(st, m_total_candidates=m_total_candidates)
        layer_2.append({
            "strategy":    strat,
            "exit_method": em,
            **st, **v,
        })
    layer_2.sort(key=lambda r: -r.get("sharpe", -999))

    # Layer 3: parameter-variant winners within exit-family
    # Family-grouping heuristics:
    FAMILIES = {
        "time_stop":  ["time_stop_10d", "time_stop_20d", "class_time_stop"],
        "r_multiple": ["r_multiple_2r", "r_multiple_3r"],
        "trailing":   ["trailing_5pct", "trailing_10pct", "trailing_15pct"],
        "atr_trail":  ["atr_trail_1x", "atr_trail_2x", "atr_trail_mae_conditional",
                       "atr_trail_vix_conditional"],
        "chandelier": ["chandelier_3x"],
        "breakeven":  ["break_even_at_1r", "breakeven_plus_trail"],
        "partial":    ["multi_tier_partial", "hybrid_50pct_target"],
    }
    layer_3 = {}
    for strat in sorted(cube["strategy"].unique()):
        per_family_winner = {}
        for fam_name, variants in FAMILIES.items():
            sub = cube[(cube["strategy"] == strat) & (cube["exit_method"].isin(variants))]
            if len(sub) < 5:
                continue
            cells = []
            for em in sub["exit_method"].unique():
                em_cell = sub[sub["exit_method"] == em]
                if len(em_cell) < 5:
                    continue
                hd = em_cell["hold_days"] if "hold_days" in em_cell.columns else None
                st = _cell_stats(em_cell["pnl_pct"], hd)
                cells.append({"exit_method": em, **st})
            if not cells:
                continue
            cells.sort(key=lambda r: -r.get("sharpe", -999))
            per_family_winner[fam_name] = {
                "winner":     cells[0]["exit_method"],
                "winner_sharpe": cells[0]["sharpe"],
                "ranked":     cells,
            }
        if per_family_winner:
            layer_3[strat] = per_family_winner

    # Top-line proposals
    proposals = []
    # Top 5 layer-1 exit methods by aggregate Sharpe (n_strats >= 5)
    ranked_em = sorted(layer_1.items(),
                       key=lambda kv: -kv[1].get("sharpe", -999))
    top_em = [em for em, d in ranked_em if d["n_strategies_paired"] >= 5][:5]
    if top_em:
        proposals.append(
            f"top-5 aggregate exit methods (n_strats>=5): {top_em}")
    # Layer-2: cells with verdict=PASS = high-confidence STRATEGY_EXIT_OVERRIDE candidates
    pass_cells = [r for r in layer_2 if r.get("verdict") == "PASS"]
    if pass_cells:
        proposals.append(
            f"{len(pass_cells)} (strategy x exit) cells PASS DEC-426 5-Gate; "
            f"top: {pass_cells[0]['strategy']} + {pass_cells[0]['exit_method']} "
            f"(Sharpe {pass_cells[0]['sharpe']})")

    return {
        "status":        "ok",
        "layer_1_per_exit_method_aggregate":  layer_1,
        "layer_2_per_strategy_exit_cell":     layer_2[:100],
        "layer_3_parameter_variant_winners":  layer_3,
        "proposals":     proposals,
    }


def write_summary_md(per_strategy_results: dict, out_path: Path,
                      producer_audit: dict | None = None,
                      exit_analysis: dict | None = None) -> None:
    """Living summary doc; owner reviews here."""
    lines = []
    lines.append("# Per-strategy optimization candidates (living)")
    lines.append("")
    lines.append("**Source (per CHECKLIST #77):** generated by `scripts/optimize_strategies_from_cube.py` per owner directive 2026-05-26. Empirical-evidence-driven; per memory `project_no_apriori_strategy_pruning.md`, all proposed changes require explicit owner approval per change before implementation.")
    lines.append("")
    lines.append(f"**Strategies analyzed:** {len(per_strategy_results)}. Per-strategy JSONs at `output_optimization_candidates/<strategy>.json`.")
    lines.append("")
    lines.append("## Per-strategy summary (sorted by Sharpe DESC)")
    lines.append("")
    lines.append("| Strategy | n | Sharpe | WR | PF | Verdict | Key proposals |")
    lines.append("|---|---:|---:|---:|---:|---|---|")
    rows = []
    for strat, data in per_strategy_results.items():
        if data.get("status") == "no_fires":
            continue
        agg = data.get("aggregate", {})
        # Collect top proposals across dimensions
        props = []
        for dim_key in ("dimension_a_thresholds", "dimension_b_compound",
                        "dimension_c_regime", "dimension_d_exit",
                        "dimension_f_universe", "dimension_g_hold",
                        "dimension_i_macro"):
            d = data.get(dim_key, {})
            if isinstance(d, dict):
                for p in d.get("proposals", [])[:1]:
                    props.append(f"{dim_key[10:14]}: {p[:80]}")
        rows.append({
            "strategy": strat,
            "n":        data.get("n_trades", 0),
            "sharpe":   agg.get("sharpe", 0),
            "wr":       round(agg.get("win_rate", 0) * 100, 1),
            "pf":       agg.get("profit_factor", 0),
            "verdict":  agg.get("verdict", "n/a"),
            "props":    " | ".join(props[:2]) if props else "(no proposals)",
        })
    rows.sort(key=lambda r: -r["sharpe"])
    for r in rows:
        lines.append(f"| {r['strategy']} | {r['n']} | {r['sharpe']} | {r['wr']}% | {r['pf']} | {r['verdict']} | {r['props']} |")
    lines.append("")
    # Batch 389: producer-zero re-audit section
    if producer_audit:
        s = producer_audit.get("summary", {})
        lines.append("## Producer-zero re-audit (Batch 389)")
        lines.append("")
        lines.append(f"Active strategies: {s.get('active_count')}; fired: {s.get('fired_count')}; quiet: {s.get('quiet_count')}.")
        lines.append("")
        lines.append("Quiet-strategy classification:")
        lines.append("")
        lines.append("| Bucket | Count | Meaning |")
        lines.append("|---|---:|---|")
        lines.append(f"| PRODUCER_LAYER_ZERO_LIKELY | {s.get('PRODUCER_LAYER_ZERO_LIKELY', 0)} | Gate keys never emit truthy values; producer-side gap |")
        lines.append(f"| COMPOUND_RESTRICTIVE       | {s.get('COMPOUND_RESTRICTIVE', 0)} | Individual clauses emit but AND-compound never satisfies |")
        lines.append(f"| SKIPPED_AT_ENGINE          | {s.get('SKIPPED_AT_ENGINE', 0)} | Produces candidates; engine gate filters them (likely a remaining gate) |")
        lines.append("")
        priority = producer_audit.get("priority_families", {})
        if priority:
            lines.append("**Priority producer-fix families** (n>=3 strategies sharing same missing key):")
            lines.append("")
            lines.append("| Missing producer key | Strategies affected | Action |")
            lines.append("|---|---:|---|")
            for key, strats in sorted(priority.items(), key=lambda kv: -len(kv[1])):
                lines.append(f"| `{key}` | {len(strats)} | Audit producer module; emit key OR loosen consumer compound |")
            lines.append("")
    # Batch 391: exit-method optimization section
    if exit_analysis and exit_analysis.get("status") == "ok":
        lines.append("## Exit-method optimization (Batch 391)")
        lines.append("")
        l1 = exit_analysis.get("layer_1_per_exit_method_aggregate", {})
        if l1:
            lines.append("### Layer 1 - exit methods ranked by aggregate Sharpe (across all paired strategies)")
            lines.append("")
            lines.append("| Exit method | n_strategies | n_cells | Sharpe | WR | PF | 5-gate |")
            lines.append("|---|---:|---:|---:|---:|---:|---|")
            ranked = sorted(l1.items(), key=lambda kv: -kv[1].get("sharpe", -999))
            for em, d in ranked[:15]:
                lines.append(
                    f"| `{em}` | {d.get('n_strategies_paired', 0)} | {d.get('n', 0)} | "
                    f"{d.get('sharpe', 0)} | {round(d.get('win_rate', 0)*100, 1)}% | "
                    f"{d.get('profit_factor', 0)} | "
                    f"{'PASS' if d.get('five_gate_pass') else d.get('verdict', 'n/a')} |"
                )
            lines.append("")
        l2 = exit_analysis.get("layer_2_per_strategy_exit_cell", [])
        if l2:
            pass_cells = [r for r in l2 if r.get("verdict") == "PASS"]
            lines.append(f"### Layer 2 - top 10 (strategy x exit) cells by Sharpe (of {len(l2)} cells with n>=5; {len(pass_cells)} PASS 5-Gate)")
            lines.append("")
            lines.append("| Strategy | Exit | n | Sharpe | WR | PF | 5-gate |")
            lines.append("|---|---|---:|---:|---:|---:|---|")
            for r in l2[:10]:
                lines.append(
                    f"| {r['strategy']} | `{r['exit_method']}` | {r['n']} | {r['sharpe']} | "
                    f"{round(r.get('win_rate', 0)*100, 1)}% | {r.get('profit_factor', 0)} | "
                    f"{'PASS' if r.get('five_gate_pass') else r.get('verdict', 'n/a')} |"
                )
            lines.append("")
        l3 = exit_analysis.get("layer_3_parameter_variant_winners", {})
        if l3:
            lines.append("### Layer 3 - parameter-variant winners within exit-family (per strategy)")
            lines.append("")
            for strat in sorted(l3.keys())[:10]:
                lines.append(f"**{strat}**:")
                for fam_name, info in l3[strat].items():
                    lines.append(f"- `{fam_name}` family winner: `{info['winner']}` (Sharpe {info['winner_sharpe']})")
                lines.append("")
        for p in exit_analysis.get("proposals", []):
            lines.append(f"- {p}")
        lines.append("")
    lines.append("## Approval pattern")
    lines.append("")
    lines.append("Owner reviews per-strategy JSON + this summary. For each candidate change, owner directs me to apply via a separate batch. NEVER apply changes directly from this output - all changes require explicit per-change owner approval per `project_no_apriori_strategy_pruning.md`.")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", default="output_phase_1a_beta_single_local",
                    help="Phase 1A-beta output dir containing trade_log + cube + verdict_cube")
    ap.add_argument("--output-dir", default="output_optimization_candidates")
    ap.add_argument("--strategy", default=None,
                    help="Only analyze this single strategy (default: all fired strategies)")
    # B1392 (2026-07-26, owner-approved): IS-WINDOW RESTRICTION. Without this the
    # optimizer reads the WHOLE cube including the holdout fold, so any entry-gate change
    # it motivates would have been informed by the very data the next run is graded on --
    # fit-and-test-on-the-same-data, which voids the verdict. Restricting the optimizer's
    # input to the in-sample window keeps the holdout genuinely unseen by every selection
    # decision. Defaults are the DEC-505 IS window (folds 1-3).
    ap.add_argument("--is-start", default="2022-05-05",
                    help="IS window start (inclusive), YYYY-MM-DD. Rows before this are dropped.")
    ap.add_argument("--is-end", default="2025-05-05",
                    help="IS window end (EXCLUSIVE), YYYY-MM-DD. This is the holdout boundary: "
                         "entries on/after it are dropped so the holdout stays unseen.")
    ap.add_argument("--no-is-filter", action="store_true",
                    help="DANGEROUS: analyze the full cube including the holdout fold. Only for "
                         "post-hoc forensics, NEVER for deriving gate changes that a later run grades.")
    args = ap.parse_args()

    in_dir = REPO / args.input_dir
    out_dir = REPO / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if not (in_dir / "trade_log.csv").exists():
        print(f"[ERROR] {in_dir / 'trade_log.csv'} not found")
        return 1

    print(f"[INFO] Loading from {in_dir}")
    trade_log = pd.read_csv(in_dir / "trade_log.csv", low_memory=False)
    cube_path = in_dir / "trade_exit_detail.csv"
    cube = pd.read_csv(cube_path, low_memory=False) if cube_path.exists() else pd.DataFrame()

    def _is_filter(df: pd.DataFrame, label: str) -> pd.DataFrame:
        """B1392: drop everything outside the IS window so the holdout is never an input
        to a gate decision. Fails LOUD if entry_date is missing - silently analyzing the
        full window would be the exact contamination this flag exists to prevent."""
        if df.empty:
            return df
        if "entry_date" not in df.columns:
            raise SystemExit(f"[FATAL] {label} has no entry_date column; cannot apply the "
                             f"IS-window filter. Refusing to run un-filtered (use "
                             f"--no-is-filter only for forensics).")
        d = pd.to_datetime(df["entry_date"], errors="coerce")
        keep = (d >= pd.Timestamp(args.is_start)) & (d < pd.Timestamp(args.is_end))
        out = df[keep].copy()
        print(f"[IS-FILTER] {label}: {len(df):,} -> {len(out):,} rows "
              f"({args.is_start} <= entry_date < {args.is_end}); "
              f"{len(df) - len(out):,} holdout/out-of-window rows EXCLUDED")
        return out

    if args.no_is_filter:
        print("[WARN] --no-is-filter: analyzing the FULL window INCLUDING the holdout. "
              "Any gate change derived from this run is contaminated and must NOT be "
              "graded by a later run on the same window.")
    else:
        trade_log = _is_filter(trade_log, "trade_log")
        cube = _is_filter(cube, "cube")
        if trade_log.empty:
            print("[ERROR] IS filter removed every trade_log row - check --is-start/--is-end")
            return 1
    screener_source = (REPO / "backtest" / "signals" / "screener.py").read_text(encoding="utf-8")

    fired = sorted(trade_log["strategy"].unique()) if not args.strategy else [args.strategy]
    print(f"[INFO] {len(fired)} strategies to analyze")

    # Bonferroni denominator: total candidates across all strategies + dimensions
    # Conservative estimate: ~3-5 candidates per strategy x 9 dimensions
    M = max(len(fired) * 9, 1)

    results = {}
    for strat in fired:
        print(f"  - {strat}", end=" ")
        try:
            r = optimize_strategy(strat, trade_log, cube, screener_source, M)
            results[strat] = r
            json_path = out_dir / f"{strat}.json"
            json_path.write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")
            print(f"-> {json_path.name}")
        except Exception as exc:
            print(f"[FAIL] exc={exc}")
            results[strat] = {"strategy": strat, "status": "error", "error": str(exc)}

    # Batch 389: post-cube producer-zero re-audit
    skipped_path = in_dir / "skipped_trades.csv"
    skipped_df = pd.read_csv(skipped_path, low_memory=False) if skipped_path.exists() else pd.DataFrame()
    print(f"\n[INFO] Producer-zero re-audit against {len(skipped_df)} skipped rows...")
    producer_audit = producer_zero_reaudit(trade_log, skipped_df, screener_source)
    producer_audit_path = out_dir / "producer_zero_post_cube_audit.json"
    producer_audit_path.write_text(json.dumps(producer_audit, indent=2, default=str),
                                    encoding="utf-8")
    s = producer_audit["summary"]
    print(f"[OK] Producer-zero re-audit: active={s['active_count']}, "
          f"fired={s['fired_count']}, quiet={s['quiet_count']}")
    print(f"     PRODUCER_LAYER_ZERO_LIKELY: {s['PRODUCER_LAYER_ZERO_LIKELY']}")
    print(f"     COMPOUND_RESTRICTIVE:       {s['COMPOUND_RESTRICTIVE']}")
    print(f"     SKIPPED_AT_ENGINE:          {s['SKIPPED_AT_ENGINE']}")
    if producer_audit.get("priority_families"):
        print(f"     Priority families (n>=3):")
        for k, strats in sorted(producer_audit["priority_families"].items(),
                                 key=lambda kv: -len(kv[1])):
            print(f"       {k} -> {len(strats)} strategies")

    # Batch 391: exit-method optimization at (strategy x exit) cell level
    print(f"\n[INFO] Exit-method analysis (Layer 1-2-3)...")
    exit_analysis = analyze_exit_methods(cube, M)
    if exit_analysis.get("status") == "ok":
        exit_path = out_dir / "exit_method_analysis.json"
        exit_path.write_text(json.dumps(exit_analysis, indent=2, default=str),
                              encoding="utf-8")
        n_l1 = len(exit_analysis.get("layer_1_per_exit_method_aggregate", {}))
        n_l2 = len(exit_analysis.get("layer_2_per_strategy_exit_cell", []))
        n_l3 = len(exit_analysis.get("layer_3_parameter_variant_winners", {}))
        print(f"[OK] Exit analysis: {n_l1} exits / {n_l2} (strat x exit) cells / "
              f"{n_l3} strategies w/ family-variant winners")
        print(f"[OK] Exit analysis JSON: {exit_path.relative_to(REPO)}")
    else:
        print(f"[WARN] Exit analysis skipped: {exit_analysis.get('status')}")

    summary_path = out_dir / "optimization_summary.md"
    write_summary_md(results, summary_path, producer_audit=producer_audit,
                     exit_analysis=exit_analysis if exit_analysis.get("status") == "ok" else None)
    print(f"\n[OK] {len(results)} strategies analyzed")
    print(f"[OK] Per-strategy JSONs: {out_dir}/<strategy>.json")
    print(f"[OK] Producer audit:     {producer_audit_path.relative_to(REPO)}")
    print(f"[OK] Living summary:     {summary_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
