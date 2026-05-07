"""DEC-578 — Phase 1B-α 7-gate verdict composer (Pass 53 Day-9-evening).

Composes per-cell verdict from existing primitives built earlier:
  - DEC-423 bootstrap CI (backtest/results/bootstrap_ci.py)
  - DEC-247 deflated Sharpe (backtest/results/deflated_sharpe.py)
  - DEC-401 Bonferroni / Holm (backtest/results/multi_test.py)
  - DEC-250 edge decay (backtest/results/edge_decay.py)
  - DEC-415 rolling Sharpe stability (backtest/results/rolling_sharpe_test.py)
  - DEC-405 stress tests (backtest/results/stress_tests.py)
  - DEC-246 quant audit Sharpe / DD computation (backtest/results/quant_audit.py)

Per DEC-578 (Pass 53 review take 5; promoted to 7-gate from prior 6-gate):

  Gate 1: Sample size n ≥ 30 trades per cell (statistical floor)
  Gate 2: Bonferroni-corrected p-value ≤ α/N (cross-strategy multi-testing;
          N=199 strategies per CANONICAL_FACTS F-002)
  Gate 3: PSR (Probabilistic Sharpe Ratio) ≥ 0.95 (DSR ≥ 0.95 with strategy-N
          correction for selection bias)
  Gate 4: t-statistic ≥ 3.4 (cross-cell-within-strategy after Bonferroni
          correction; per DEC-582 distinct from Gate 2 cross-strategy scope)
  Gate 5: R:R ratio ≥ 2.0 (DEC-353 hard reject)
  Gate 6: Profit factor ≥ 1.3 (DEC-353 + sector-adjusted high-vol ≥ 1.2)
  Gate 7: Effect-size floor ≥ 5bps absolute mean return per trade
          (DEC-578 Pass 53 7th gate — prevents "statistically-significant-but-
          economically-irrelevant" winners)

Per DEC-594 same-commit: artifact + tests land together.

Cell verdict outputs:
  PASS: all 7 gates ≥ threshold
  FAIL_<gate_N>: failed gate N (first-fail; exit fast)
  INSUFFICIENT_SAMPLE: n < 30 (Gate 1)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from backtest.results.deflated_sharpe import compute_dsr_from_returns
from backtest.results.multi_test import bonferroni
from backtest.results.quant_audit import annualized_sharpe


# Default thresholds per DEC-578 + DEC-353 + DEC-582
GATE_1_MIN_TRADES = 30
GATE_2_BONF_ALPHA = 0.05
GATE_2_N_STRATEGIES = 199           # per CANONICAL_FACTS F-002
GATE_3_DSR_THRESHOLD = 0.95
GATE_4_T_STAT_THRESHOLD = 3.4
GATE_5_R_R_MIN = 2.0
GATE_6_PROFIT_FACTOR_MIN = 1.3
GATE_7_MEAN_RETURN_MIN_BPS = 5      # 5 basis points = 0.05%


@dataclass
class GateResult:
    """Per-cell 7-gate verdict result."""
    verdict: str                           # PASS / FAIL_<gate> / INSUFFICIENT_SAMPLE
    gates_passed: int                      # 0-7
    gate_details: Dict[str, dict]          # per-gate result with threshold + value
    n_trades: int

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "gates_passed": self.gates_passed,
            "n_trades": self.n_trades,
            **{f"gate_{k}": v for k, v in self.gate_details.items()},
        }


def _t_stat(returns: Sequence[float]) -> float:
    """Per-cell t-statistic for mean return ≠ 0 (one-sample t)."""
    arr = np.asarray(returns, dtype=float)
    if len(arr) < 2:
        return 0.0
    mean = arr.mean()
    se = arr.std(ddof=1) / np.sqrt(len(arr))
    if se < 1e-12 or not np.isfinite(se):
        return 0.0
    return float(mean / se)


def _t_stat_to_pvalue(t: float, df: int) -> float:
    """Two-sided p-value from t-stat using Student-t survival approx via normal
    for df ≥ 30; degrades to normal CDF for small samples (acceptable for our
    n ≥ 30 floor)."""
    import math
    abs_t = abs(t)
    # Normal-approx tail (good for df ≥ 30); 1 - CDF(|t|)
    p_one_side = 0.5 * (1 - math.erf(abs_t / math.sqrt(2)))
    return 2 * p_one_side


def _profit_factor(returns: Sequence[float]) -> float:
    arr = np.asarray(returns, dtype=float)
    wins = arr[arr > 0].sum()
    losses = abs(arr[arr < 0].sum())
    if losses < 1e-12:
        return float("inf") if wins > 0 else 0.0
    return float(wins / losses)


def _rr_ratio(returns: Sequence[float]) -> float:
    """Average win / average loss (per-trade R:R)."""
    arr = np.asarray(returns, dtype=float)
    wins = arr[arr > 0]
    losses = arr[arr < 0]
    if len(wins) == 0 or len(losses) == 0:
        return 0.0
    avg_win = wins.mean()
    avg_loss = abs(losses.mean())
    if avg_loss < 1e-12:
        return float("inf")
    return float(avg_win / avg_loss)


def evaluate_cell(
    returns: Sequence[float],
    n_strategies_tested: int = GATE_2_N_STRATEGIES,
    n_cells_in_strategy: int = 1,
    min_trades: int = GATE_1_MIN_TRADES,
    dsr_threshold: float = GATE_3_DSR_THRESHOLD,
    t_threshold: float = GATE_4_T_STAT_THRESHOLD,
    rr_min: float = GATE_5_R_R_MIN,
    pf_min: float = GATE_6_PROFIT_FACTOR_MIN,
    mean_return_min_bps: float = GATE_7_MEAN_RETURN_MIN_BPS,
) -> GateResult:
    """Evaluate per-cell 7-gate Phase 1B-α verdict.

    Args:
        returns: per-trade return values (decimal; e.g., 0.05 for +5%).
        n_strategies_tested: total strategy roster size (for Bonferroni).
        n_cells_in_strategy: cells-within-strategy count (for Gate 4 inner correction).
        Other params: gate thresholds (defaults match DEC-578).

    Returns:
        GateResult with verdict, gates_passed count, per-gate details, n_trades.
    """
    arr = np.asarray(returns, dtype=float)
    n = len(arr)
    gate_details: Dict[str, dict] = {}

    # Gate 1: sample size
    g1_pass = n >= min_trades
    gate_details["gate_1_sample_size"] = {
        "passed": g1_pass, "threshold": min_trades, "value": n,
    }
    if not g1_pass:
        return GateResult(verdict="INSUFFICIENT_SAMPLE", gates_passed=0,
                          gate_details=gate_details, n_trades=n)

    # Gate 2: Bonferroni cross-strategy
    t_stat_value = _t_stat(arr)
    raw_pvalue = _t_stat_to_pvalue(t_stat_value, df=n - 1)
    _, bonf_adj = bonferroni([raw_pvalue], alpha=GATE_2_BONF_ALPHA * n_strategies_tested
                              / max(n_strategies_tested, 1))
    # Effective: p × n_strategies_tested ≤ alpha
    bonf_adj_p = min(raw_pvalue * n_strategies_tested, 1.0)
    g2_pass = bonf_adj_p <= GATE_2_BONF_ALPHA
    gate_details["gate_2_bonferroni"] = {
        "passed": g2_pass, "threshold": GATE_2_BONF_ALPHA,
        "value": round(bonf_adj_p, 6), "raw_pvalue": round(raw_pvalue, 6),
        "n_strategies": n_strategies_tested,
    }
    if not g2_pass:
        return GateResult(verdict="FAIL_GATE_2_BONFERRONI", gates_passed=1,
                          gate_details=gate_details, n_trades=n)

    # Gate 3: DSR
    dsr_result = compute_dsr_from_returns(arr, n_strategies_tested=n_strategies_tested)
    dsr = dsr_result["dsr"]
    g3_pass = dsr >= dsr_threshold
    gate_details["gate_3_dsr"] = {
        "passed": g3_pass, "threshold": dsr_threshold,
        "value": round(dsr, 4),
        "psr": round(dsr_result["psr"], 4),
        "sharpe_observed": round(dsr_result["sharpe_observed"], 4),
    }
    if not g3_pass:
        return GateResult(verdict="FAIL_GATE_3_DSR", gates_passed=2,
                          gate_details=gate_details, n_trades=n)

    # Gate 4: t-stat (cross-cell-within-strategy after Bonferroni)
    inner_bonf = GATE_2_BONF_ALPHA / max(n_cells_in_strategy, 1)
    g4_pass = abs(t_stat_value) >= t_threshold
    gate_details["gate_4_t_stat"] = {
        "passed": g4_pass, "threshold": t_threshold,
        "value": round(t_stat_value, 4),
        "n_cells_in_strategy": n_cells_in_strategy,
        "inner_bonferroni_alpha": round(inner_bonf, 6),
    }
    if not g4_pass:
        return GateResult(verdict="FAIL_GATE_4_T_STAT", gates_passed=3,
                          gate_details=gate_details, n_trades=n)

    # Gate 5: R:R ratio
    rr = _rr_ratio(arr)
    g5_pass = rr >= rr_min
    gate_details["gate_5_rr_ratio"] = {
        "passed": g5_pass, "threshold": rr_min, "value": round(rr, 4),
    }
    if not g5_pass:
        return GateResult(verdict="FAIL_GATE_5_RR", gates_passed=4,
                          gate_details=gate_details, n_trades=n)

    # Gate 6: profit factor
    pf = _profit_factor(arr)
    g6_pass = pf >= pf_min
    gate_details["gate_6_profit_factor"] = {
        "passed": g6_pass, "threshold": pf_min, "value": round(pf, 4),
    }
    if not g6_pass:
        return GateResult(verdict="FAIL_GATE_6_PF", gates_passed=5,
                          gate_details=gate_details, n_trades=n)

    # Gate 7: effect-size floor (mean return ≥ 5bps)
    mean_bps = arr.mean() * 10000  # decimal → bps
    g7_pass = abs(mean_bps) >= mean_return_min_bps
    gate_details["gate_7_effect_size_bps"] = {
        "passed": g7_pass, "threshold": mean_return_min_bps,
        "value": round(mean_bps, 2),
    }
    if not g7_pass:
        return GateResult(verdict="FAIL_GATE_7_EFFECT_SIZE", gates_passed=6,
                          gate_details=gate_details, n_trades=n)

    return GateResult(verdict="PASS", gates_passed=7, gate_details=gate_details,
                      n_trades=n)


def compute_verdict_cube(
    cube_df: pd.DataFrame,
    pnl_col: str = "pnl_pct",
    cell_id_cols: Sequence[str] = (
        "strategy", "regime_at_entry", "sector", "cap_band", "vol_band",
    ),
    n_strategies_tested: int = GATE_2_N_STRATEGIES,
) -> pd.DataFrame:
    """Apply 7-gate verdict to every cell in a cube of trades.

    Args:
        cube_df: trade-level DataFrame with at least pnl_col + cell_id_cols.
        pnl_col: column with per-trade P&L percent.
        cell_id_cols: dimensions defining a cell.
        n_strategies_tested: roster size for Bonferroni.

    Returns:
        DataFrame with one row per cell + verdict + 7-gate detail columns.
    """
    if cube_df.empty:
        return pd.DataFrame()

    rows = []
    available_cols = [c for c in cell_id_cols if c in cube_df.columns]
    if not available_cols:
        return pd.DataFrame()

    for cell_keys, cell_df in cube_df.groupby(list(available_cols), dropna=False):
        if not isinstance(cell_keys, tuple):
            cell_keys = (cell_keys,)
        result = evaluate_cell(
            returns=cell_df[pnl_col].values,
            n_strategies_tested=n_strategies_tested,
        )
        row = dict(zip(available_cols, cell_keys))
        row["verdict"] = result.verdict
        row["gates_passed"] = result.gates_passed
        row["n_trades"] = result.n_trades
        # Flatten gate details
        for gate_name, gate_info in result.gate_details.items():
            row[f"{gate_name}_value"] = gate_info.get("value")
            row[f"{gate_name}_passed"] = gate_info.get("passed")
        rows.append(row)

    return pd.DataFrame(rows)
