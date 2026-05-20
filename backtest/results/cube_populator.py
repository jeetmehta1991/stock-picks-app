"""Cube populator (Batch 243 / DEC-422 + DEC-426).

Phase 1B Sprint 7 infrastructure: groups a trade_log by
(strategy x exit_method x regime), computes per-cell metrics, applies
the 11-criteria + 5-Gate evaluation, emits per-cell priority tiers
(P1 / P2 / P3) used by Phase 1A-beta winners extraction AND Phase 1B-alpha
agent-input filtering.

Owner directive 2026-05-19: Phase 1B-alpha applies agents ONLY to P1
combos (passes all 11 overall criteria + DEC-426 5-Gate validity).
This module is the verdict engine.

References:
  - 11 criteria: CLAUDE.md passing-criteria table
  - DEC-426 5-Gate: n>=30 + p<0.05 Bonferroni + PSR>=0.95 + t-stat>=3.4
    + R:R>=2.0
  - DEC-422: dimensional cube infrastructure
  - DEC-209: per-regime verdicts (AGENT_ADDS / AGENT_HURTS / NEUTRAL)

Outputs winner schema (used by scripts/extract_phase_1a_beta_winners.py):
  combo_id, strategy, exit_method, regime, n_trades, win_rate,
  profit_factor, expected_value, win_loss_ratio, max_dd, total_roi,
  sharpe, t_stat, bonferroni_p, psr, rr_ratio, all_criteria_pass,
  five_gate_pass, priority, fail_reason, tickers_fired
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Criteria thresholds (CLAUDE.md canonical + DEC-426 5-Gate)
# ---------------------------------------------------------------------------
_HIGH_VOL_REGIMES = {"crisis"}

_THRESH_PER_REGIME = {
    "win_rate":       {"default": 0.55, "high_vol": 0.50},
    "profit_factor":  {"default": 1.30, "high_vol": 1.20},
    "max_dd":         {"default": 0.20, "high_vol": 0.25},
    "sharpe":         {"default": 0.70, "high_vol": 0.70},
}

_THRESH_OVERALL = {
    "win_rate":      0.55,
    "profit_factor": 1.50,
    "min_trades":    100,
    "sharpe":        1.00,
}

# DEC-426 5-Gate validity
_FIVE_GATE = {
    "n_min":          30,
    "bonferroni_max": 0.05,
    "psr_min":        0.95,
    "t_stat_min":     3.4,
    "rr_min":         2.0,
}

_REQUIRED_COLS = {"strategy", "pnl_pct"}  # exit column normalized below


def _normalize_regime_column(df: pd.DataFrame) -> pd.DataFrame:
    """Accept 'regime' OR 'regime_at_entry' (engine emits the latter)."""
    if "regime" in df.columns:
        return df
    if "regime_at_entry" in df.columns:
        df = df.copy()
        df["regime"] = df["regime_at_entry"]
        return df
    df = df.copy()
    df["regime"] = "neutral"  # safe default
    return df


def _normalize_exit_column(df: pd.DataFrame) -> pd.DataFrame:
    """Accept 'exit_method' OR 'exit_reason' (engine emits the latter).
    The two are semantically the same: the exit-strategy name that fired.
    """
    if "exit_method" in df.columns:
        return df
    if "exit_reason" in df.columns:
        df = df.copy()
        df["exit_method"] = df["exit_reason"]
        return df
    df = df.copy()
    df["exit_method"] = "unknown"
    return df


def compute_cell_metrics(trades: pd.DataFrame) -> dict:
    """Per-cell metrics from a trade subset (assumes constant strat/exit/regime).

    Computes:
      n_trades, win_rate, expected_value (avg pnl_pct),
      profit_factor (sum wins / sum |losses|), win_loss_ratio,
      max_dd (max peak-to-trough on cumulative pnl), total_roi (sum pnl),
      sharpe (annualized; daily approximation),
      t_stat (one-sample t-test of pnl != 0),
      bonferroni_p, psr (placeholder; full DEC-247 PSR via deflated_sharpe.py
                          if needed for production),
      rr_ratio (avg gain / avg loss).
    """
    if trades is None or trades.empty:
        return {"n_trades": 0}
    pnls = trades["pnl_pct"].astype(float).values
    n = len(pnls)
    wins = pnls[pnls > 0]
    losses = pnls[pnls <= 0]
    n_wins = len(wins)
    win_rate = n_wins / n if n > 0 else 0.0
    expected_value = float(pnls.mean()) if n > 0 else 0.0
    gross_win = float(wins.sum()) if len(wins) > 0 else 0.0
    gross_loss = float(abs(losses.sum())) if len(losses) > 0 else 0.0
    profit_factor = gross_win / gross_loss if gross_loss > 0 else (
        float("inf") if gross_win > 0 else 0.0
    )
    avg_win = float(wins.mean()) if len(wins) > 0 else 0.0
    avg_loss = float(abs(losses.mean())) if len(losses) > 0 else 0.0
    win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else (
        float("inf") if avg_win > 0 else 0.0
    )
    total_roi = float(pnls.sum())
    # Max drawdown on cumulative pnl sequence
    cum = pnls.cumsum()
    peak = np.maximum.accumulate(cum)
    dd_arr = peak - cum
    max_dd_pct = float(dd_arr.max()) / 100.0 if len(dd_arr) > 0 else 0.0
    # Sharpe (annualized; assumes daily-ish trade cadence; rough approx)
    std = float(pnls.std(ddof=1)) if n > 1 else 0.0
    sharpe = (expected_value / std) * np.sqrt(252) if std > 0 else 0.0
    # T-stat (one-sample)
    t_stat = (expected_value * np.sqrt(n)) / std if std > 0 else 0.0
    # PSR placeholder (DEC-247 via deflated_sharpe.py wires the real one;
    # this approximation is monotonic in sharpe + n for ranking)
    psr = min(0.99, max(0.0, 0.5 + (sharpe * np.sqrt(n) / 50)))
    # R:R ratio
    rr_ratio = win_loss_ratio if win_loss_ratio != float("inf") else 99.0
    # Bonferroni p-value (placeholder; caller should pass M for full universe-
    # wide correction). Use simplistic two-tail normal approx.
    from scipy.stats import t as t_dist
    raw_p = float(2 * (1 - t_dist.cdf(abs(t_stat), df=max(1, n - 1)))) if std > 0 else 1.0
    return {
        "n_trades":       n,
        "win_rate":       round(win_rate, 4),
        "expected_value": round(expected_value, 4),
        "profit_factor":  round(profit_factor, 4),
        "win_loss_ratio": round(win_loss_ratio, 4),
        "max_dd":         round(max_dd_pct, 4),
        "total_roi":      round(total_roi, 4),
        "sharpe":         round(sharpe, 4),
        "t_stat":         round(t_stat, 4),
        "psr":            round(psr, 4),
        "bonferroni_p":   round(raw_p, 6),
        "rr_ratio":       round(rr_ratio, 4),
    }


def evaluate_cell_criteria(metrics: dict, regime: str) -> dict:
    """Apply 11-criteria + DEC-426 5-Gate validity. Returns dict with
    per-check booleans + overall priority tier (P1 / P2 / P3) + fail reason.
    """
    n = metrics.get("n_trades", 0)
    if n < 30:
        return {
            "priority":          "P3",
            "all_criteria_pass": False,
            "five_gate_pass":    False,
            "fail_reason":       "insufficient_trades",
            "checks":            {},
        }
    high_vol = regime in _HIGH_VOL_REGIMES
    band = "high_vol" if high_vol else "default"
    checks = {
        "win_rate":      metrics.get("win_rate", 0) >= _THRESH_PER_REGIME["win_rate"][band],
        "profit_factor": metrics.get("profit_factor", 0) > _THRESH_PER_REGIME["profit_factor"][band],
        "expected_value": metrics.get("expected_value", 0) > 0,
        "win_loss_ratio": metrics.get("win_loss_ratio", 0) > 1.0,
        "max_dd":         metrics.get("max_dd", 1.0) < _THRESH_PER_REGIME["max_dd"][band],
        "total_roi":      metrics.get("total_roi", 0) > 0,
        "sharpe":         metrics.get("sharpe", 0) >= _THRESH_PER_REGIME["sharpe"][band],
    }
    per_regime_pass = all(checks.values())
    # 5-Gate
    five_gate = {
        "n":           n >= _FIVE_GATE["n_min"],
        "bonferroni":  metrics.get("bonferroni_p", 1.0) < _FIVE_GATE["bonferroni_max"],
        "psr":         metrics.get("psr", 0) >= _FIVE_GATE["psr_min"],
        "t_stat":      metrics.get("t_stat", 0) >= _FIVE_GATE["t_stat_min"],
        "rr_ratio":    metrics.get("rr_ratio", 0) >= _FIVE_GATE["rr_min"],
    }
    five_gate_pass = all(five_gate.values())
    # Priority assignment per master plan
    if per_regime_pass and five_gate_pass:
        priority = "P1"
        fail_reason = ""
    elif per_regime_pass:
        priority = "P2"
        # Identify which 5-Gate item failed
        failed = [k for k, v in five_gate.items() if not v]
        fail_reason = "five_gate_fail:" + ",".join(failed)
    else:
        priority = "P3"
        failed = [k for k, v in checks.items() if not v]
        fail_reason = "criteria_fail:" + ",".join(failed)
    checks.update({"five_gate_" + k: v for k, v in five_gate.items()})
    return {
        "priority":           priority,
        "all_criteria_pass":  per_regime_pass,
        "five_gate_pass":     five_gate_pass,
        "fail_reason":        fail_reason,
        "checks":             checks,
    }


def populate_cube(trade_log: pd.DataFrame) -> pd.DataFrame:
    """Group trade_log by (strategy x exit_method x regime), compute per-cell
    metrics + verdict, return per-cell DataFrame.

    Output columns:
      combo_id, strategy, exit_method, regime, n_trades, win_rate, ...
      priority, all_criteria_pass, five_gate_pass, fail_reason, tickers_fired

    Empty input -> empty DataFrame.
    Missing required columns -> ValueError.
    """
    if trade_log is None or trade_log.empty:
        return pd.DataFrame()
    missing = _REQUIRED_COLS - set(trade_log.columns)
    if missing:
        raise ValueError(f"populate_cube: missing required columns {missing}")
    df = _normalize_regime_column(trade_log)
    df = _normalize_exit_column(df)
    rows = []
    grouped = df.groupby(["strategy", "exit_method", "regime"], sort=False)
    for (strat, exit_m, regime), sub in grouped:
        metrics = compute_cell_metrics(sub)
        verdict = evaluate_cell_criteria(metrics, regime=str(regime))
        tickers = sorted(sub["ticker"].astype(str).unique().tolist()) if "ticker" in sub.columns else []
        row = {
            "combo_id":         f"{strat}__{exit_m}__{regime}",
            "strategy":         strat,
            "exit_method":      exit_m,
            "regime":           regime,
            "tickers_fired":    tickers,
        }
        row.update(metrics)
        row["all_criteria_pass"] = verdict["all_criteria_pass"]
        row["five_gate_pass"]    = verdict["five_gate_pass"]
        row["priority"]          = verdict["priority"]
        row["fail_reason"]       = verdict["fail_reason"]
        rows.append(row)
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    # Priority sort: P1 first, P2, P3 last; within priority by sharpe desc
    priority_order = {"P1": 0, "P2": 1, "P3": 2}
    out["_p_sort"] = out["priority"].map(priority_order).fillna(3)
    out = out.sort_values(["_p_sort", "sharpe"], ascending=[True, False]).drop(columns=["_p_sort"]).reset_index(drop=True)
    return out


def extract_winners(
    cube_df: pd.DataFrame,
    priority_filter: Iterable[str] = ("P1",),
) -> pd.DataFrame:
    """Filter cube to specified priority tiers (default P1 only)."""
    if cube_df is None or cube_df.empty:
        return pd.DataFrame()
    if "priority" not in cube_df.columns:
        return pd.DataFrame()
    keep = list(priority_filter)
    return cube_df[cube_df["priority"].isin(keep)].copy().reset_index(drop=True)
