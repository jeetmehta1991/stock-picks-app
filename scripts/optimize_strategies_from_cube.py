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
    """Per-cell stats with Batch 375 trade-frequency Sharpe annualization."""
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
    return {
        "n":           n,
        "win_rate":    round(wr, 4),
        "mean_pp":     round(mu, 4),
        "std_pp":      round(std, 4),
        "sum_pp":      round(float(pnls.sum()), 4),
        "profit_factor": round(pf, 4),
        "sharpe":      round(sharpe, 4),
        "t_stat":      round(t_stat, 4),
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
    gates = {
        "n_>=_30":     n >= GATE_N_MIN,
        "p_<_0.05":    bonf_p < GATE_P_MAX,
        "psr_>=_0.95": False,  # placeholder; full PSR via deflated_sharpe.py (DEC-247)
        "t_>=_3.4":    stats["t_stat"] >= GATE_T_MIN,
        "rr_>=_2.0":   stats["profit_factor"] >= GATE_RR_MIN,
    }
    return {
        "verdict":         "PASS" if all([gates["n_>=_30"], gates["p_<_0.05"], gates["t_>=_3.4"], gates["rr_>=_2.0"]]) else "FAIL",
        "five_gate_pass":  all(gates.values()),
        "gates":           gates,
        "raw_p":           round(raw_p, 6),
        "bonferroni_p":    round(bonf_p, 6),
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


def write_summary_md(per_strategy_results: dict, out_path: Path,
                      producer_audit: dict | None = None) -> None:
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

    summary_path = out_dir / "optimization_summary.md"
    write_summary_md(results, summary_path, producer_audit=producer_audit)
    print(f"\n[OK] {len(results)} strategies analyzed")
    print(f"[OK] Per-strategy JSONs: {out_dir}/<strategy>.json")
    print(f"[OK] Producer audit:     {producer_audit_path.relative_to(REPO)}")
    print(f"[OK] Living summary:     {summary_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
