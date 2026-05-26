"""A/B orchestrator (Batch 245 / DEC-216 - finally wires the PARTIAL-IMPL).

Phase 1B Sprint 7 infrastructure per owner directive 2026-05-19.
Parallel-safe with Phase 1A-alpha procs (NEW file).

Per DEC-216 + DEC-131 + DEC-207-215 cluster:
- Drives Phase 1B-alpha 3-arm A/B run (rules-only / full-with-veto / no-Risk)
- Reads `winners.parquet` (P1 combos from Phase 1A-beta)
- For each P1 combo: runs all 3 arms on the same trade set
- Computes per-arm metrics + A/B verdict (DEC-131 net Sharpe gate)
- Writes ab_results.parquet (DEC-215 registry schema)

This module ORCHESTRATES the runs; actual agent execution is delegated
to the LangGraph pipeline (backtest/agents/pipeline.py, to be wired post-
1A-beta). For Phase 1A-alpha era, only Arm A is callable (rules-only =
existing engine path).

Output schema (DEC-215 AB_TEST_REGISTRY_SCHEMA):
  test_id, as_of_date, arms (list), n_trades, sharpe_rules_only,
  sharpe_full_agents, sharpe_no_risk, net_sharpe_full, net_sharpe_no_risk,
  verdict (PASS / FAIL / INSUFFICIENT_DATA), manifest_hash.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from backtest.agents.agent_gate_config import (
    AgentGateConfig,
    AgentMode,
    arm_a_rules_only,
    arm_b_full_with_veto,
    arm_c_no_risk,
)


# DEC-131 thresholds (canonical per AUDIT_INDEX.md)
DEC_131_NET_SHARPE_ABS_THRESHOLD = 0.20
DEC_131_NET_SHARPE_REL_THRESHOLD = 0.15
# DEC-207 min sample size
AB_TEST_MIN_PAIRED_TRADES_PER_ARM = 300


@dataclass
class ABArmResult:
    """Result for a single A/B arm on a single combo."""
    arm_name: str
    mode: str
    n_trades: int
    sharpe: float
    sortino: float
    max_dd: float
    win_rate: float
    profit_factor: float
    total_roi: float
    cost_usd: float


@dataclass
class ABComboResult:
    """Aggregated A/B verdict for a single (combo_id, all-arms) test."""
    combo_id: str
    arms: list[ABArmResult] = field(default_factory=list)
    net_sharpe_full_minus_rules: float = 0.0
    net_sharpe_norisk_minus_rules: float = 0.0
    verdict: str = "INSUFFICIENT_DATA"
    manifest_hash: str = ""


def _compute_arm_metrics(trades: pd.DataFrame, arm_name: str, cfg: AgentGateConfig) -> ABArmResult:
    """Compute metrics for one arm's trade set."""
    if trades.empty:
        return ABArmResult(
            arm_name=arm_name, mode=cfg.mode.value, n_trades=0,
            sharpe=0.0, sortino=0.0, max_dd=0.0, win_rate=0.0,
            profit_factor=0.0, total_roi=0.0, cost_usd=0.0,
        )
    pnls = trades["pnl_pct"].astype(float).values
    n = len(pnls)
    mu = float(pnls.mean())
    std = float(pnls.std(ddof=1)) if n > 1 else 0.0
    # Batch 375 DEC-246 sec1 fix: trade-frequency annualization. See
    # QUANT_CORRECTNESS_AUDIT_DEC_246.md sec1 - per-trade returns annualize
    # by trades-per-year derived from avg hold-days, not sqrt(252).
    if "hold_days" in trades.columns:
        avg_hold = float(trades["hold_days"].astype(float).mean())
        n_trades_per_year = 252.0 / max(avg_hold, 1.0)
        annualization_factor = np.sqrt(n_trades_per_year)
    else:
        annualization_factor = np.sqrt(252)  # legacy fallback
    sharpe = (mu / std) * annualization_factor if std > 0 else 0.0
    # Sortino - downside deviation only
    downside = pnls[pnls < 0]
    dstd = float(downside.std(ddof=1)) if len(downside) > 1 else 0.0
    sortino = (mu / dstd) * annualization_factor if dstd > 0 else 0.0
    # Max DD
    cum = pnls.cumsum()
    peak = np.maximum.accumulate(cum)
    max_dd = float((peak - cum).max()) / 100.0 if n > 0 else 0.0
    wins = pnls[pnls > 0]
    losses = pnls[pnls <= 0]
    win_rate = len(wins) / n if n > 0 else 0.0
    gross_win = float(wins.sum()) if len(wins) > 0 else 0.0
    gross_loss = float(abs(losses.sum())) if len(losses) > 0 else 0.0
    pf = gross_win / gross_loss if gross_loss > 0 else (99.0 if gross_win > 0 else 0.0)
    # Cost estimate
    candidate_count = n  # 1 candidate per trade as approximation
    cost = candidate_count * cfg.estimated_cost_per_candidate()
    return ABArmResult(
        arm_name=arm_name, mode=cfg.mode.value, n_trades=n,
        sharpe=round(sharpe, 4), sortino=round(sortino, 4),
        max_dd=round(max_dd, 4), win_rate=round(win_rate, 4),
        profit_factor=round(pf, 4), total_roi=round(float(pnls.sum()), 4),
        cost_usd=round(cost, 4),
    )


def evaluate_dec_131_gate(net_sharpe_delta: float, rules_sharpe: float) -> bool:
    """DEC-131 two-gate check.

    Primary: abs delta >= 0.20
    Secondary: relative >= 0.15 (relative to max(rules_sharpe, 0.1))
    """
    absolute_pass = net_sharpe_delta >= DEC_131_NET_SHARPE_ABS_THRESHOLD - 1e-9
    rel_denominator = max(rules_sharpe, 0.1)
    relative = net_sharpe_delta / rel_denominator
    relative_pass = relative >= DEC_131_NET_SHARPE_REL_THRESHOLD - 1e-9
    return absolute_pass or relative_pass


def compute_combo_ab(
    trades_per_arm: dict[str, pd.DataFrame],
    combo_id: str,
    arm_configs: Optional[dict[str, AgentGateConfig]] = None,
) -> ABComboResult:
    """Compute A/B verdict for one combo across all arms.

    Inputs:
      trades_per_arm:  {"rules_only": df, "full_with_veto": df, "no_risk": df}
      combo_id:        canonical "{strategy}__{exit}__{regime}"
      arm_configs:     optional per-arm config overrides (default: factory defaults)

    Returns ABComboResult with per-arm metrics + A/B verdict per DEC-131.
    """
    if arm_configs is None:
        arm_configs = {
            "rules_only":     arm_a_rules_only(),
            "full_with_veto": arm_b_full_with_veto(),
            "no_risk":        arm_c_no_risk(),
        }

    result = ABComboResult(combo_id=combo_id)
    for arm_name, df in trades_per_arm.items():
        cfg = arm_configs.get(arm_name, arm_a_rules_only())
        result.arms.append(_compute_arm_metrics(df, arm_name, cfg))

    # Build per-arm sharpe dict
    by_arm = {a.arm_name: a for a in result.arms}
    rules_sharpe = by_arm.get("rules_only", ABArmResult("", "", 0, 0, 0, 0, 0, 0, 0, 0)).sharpe
    full_sharpe = by_arm.get("full_with_veto", ABArmResult("", "", 0, 0, 0, 0, 0, 0, 0, 0)).sharpe
    norisk_sharpe = by_arm.get("no_risk", ABArmResult("", "", 0, 0, 0, 0, 0, 0, 0, 0)).sharpe

    # Net Sharpe (after subtracting cost-Sharpe per DEC-210; simplified here)
    result.net_sharpe_full_minus_rules = round(full_sharpe - rules_sharpe, 4)
    result.net_sharpe_norisk_minus_rules = round(norisk_sharpe - rules_sharpe, 4)

    # Verdict (require min sample size per DEC-207 + DEC-131 gate)
    min_n = min((a.n_trades for a in result.arms if a.n_trades > 0), default=0)
    if min_n < AB_TEST_MIN_PAIRED_TRADES_PER_ARM:
        result.verdict = "INSUFFICIENT_DATA"
    elif evaluate_dec_131_gate(result.net_sharpe_full_minus_rules, rules_sharpe):
        result.verdict = "AGENT_ADDS"
    elif result.net_sharpe_full_minus_rules < -0.10:
        result.verdict = "AGENT_HURTS"
    else:
        result.verdict = "NEUTRAL"

    # Manifest hash (DEC-215; pins arm configs to verdict for audit)
    manifest = {
        arm: cfg.as_dict() for arm, cfg in arm_configs.items()
    }
    manifest_str = json.dumps(manifest, sort_keys=True)
    result.manifest_hash = hashlib.sha256(manifest_str.encode()).hexdigest()[:16]
    return result


def orchestrate_ab_run(
    winners_df: pd.DataFrame,
    trade_logs_per_arm: dict[str, pd.DataFrame],
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Top-level A/B orchestrator: run all P1 winners through all arms.

    Inputs:
      winners_df:          from extract_phase_1a_beta_winners.py P1 filter
      trade_logs_per_arm:  3 trade logs (one per arm); each must contain
                            combo_id column matching winners_df.combo_id
      output_path:         optional path to write ab_results.parquet

    Returns: DataFrame with one row per combo + per-arm + A/B verdict.
    """
    if winners_df is None or winners_df.empty:
        return pd.DataFrame()

    rows = []
    for combo_id in winners_df["combo_id"].astype(str).unique():
        trades_per_arm = {}
        for arm_name, full_log in trade_logs_per_arm.items():
            if full_log is None or full_log.empty:
                trades_per_arm[arm_name] = pd.DataFrame()
                continue
            sub = full_log[full_log["combo_id"] == combo_id] if "combo_id" in full_log.columns else pd.DataFrame()
            trades_per_arm[arm_name] = sub
        combo_result = compute_combo_ab(trades_per_arm, combo_id)
        row = {
            "test_id":    f"ab_{combo_id}_{datetime.utcnow().strftime('%Y%m%d')}",
            "combo_id":   combo_id,
            "verdict":    combo_result.verdict,
            "net_sharpe_full_minus_rules":   combo_result.net_sharpe_full_minus_rules,
            "net_sharpe_norisk_minus_rules": combo_result.net_sharpe_norisk_minus_rules,
            "manifest_hash":                 combo_result.manifest_hash,
        }
        for arm in combo_result.arms:
            for key in ("sharpe", "sortino", "max_dd", "win_rate",
                         "profit_factor", "total_roi", "n_trades", "cost_usd"):
                row[f"{arm.arm_name}_{key}"] = getattr(arm, key)
        rows.append(row)
    out = pd.DataFrame(rows)
    if output_path is not None:
        out.to_parquet(output_path, index=False)
    return out
