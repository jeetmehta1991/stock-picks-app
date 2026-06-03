"""
scripts/build_dashboard_phase_1a.py — Phase 1A Trade Summary Dashboard data emitter.

Source of truth (per CHECKLIST #77): output_v2/* artifacts produced by
backtest/run_phase1a.py (writer.py). This script collects them into a
single data.js consumed by dashboard_phase_1a/index.html.

Per DETAILED_PROJECT_PLAN.md §7.6 Sprint 6.5 spec: 9 tabs port of legacy
analysis_dashboard_1a.html.

Run:
  python scripts/build_dashboard_phase_1a.py
Output:
  dashboard_phase_1a/data.js     (const STAGE2_DATA = ...; for browser <script>)
  dashboard_phase_1a/data.json   (same payload, plain JSON)
  dashboard_phase_1a/last_run.txt
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
# Batch 180: support --source flag for swapping between output_v2 (dev-mode
# canonical AAPL 130-day backtest) and richer runs (smoke v4, dress rehearsal).
# Default remains output_v2 for compatibility with the canonical regen flow.
import argparse
_parser = argparse.ArgumentParser()
_parser.add_argument("--source", default="output_v2",
                     help="Source output directory (e.g. output_smoke_v4_cross_regime)")
_parser.add_argument("--optimizer-dir", default="output_optimization_candidates_2026_05_28",
                     help="Batch 419: cube-optimizer output dir (per-strategy "
                          "JSONs + exit_method_analysis + producer_zero audit + "
                          "optimization_summary.md). Empty / non-existent = "
                          "Batch 419 tabs rendered as 'no data'.")
_args, _ = _parser.parse_known_args()
OUT_DIR = REPO / _args.source
OPT_DIR = REPO / _args.optimizer_dir
DASH = REPO / "dashboard_phase_1a"
DASH.mkdir(parents=True, exist_ok=True)


def load_csv(name: str, head: int | None = None) -> list[dict]:
    p = OUT_DIR / name
    if not p.exists():
        return []
    try:
        df = pd.read_csv(p)
    except Exception:
        return []
    if head is not None:
        df = df.head(head)
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def load_json(name: str) -> dict | list:
    p = OUT_DIR / name
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_iteration_rounds() -> dict:
    """Batch 443 (2026-05-29): load the persistent cube rounds registry
    at archive/cube_rounds/rounds.json. Returns a dict with the rounds
    list + a per-round cell-level Sharpe / n / verdict lookup so Tab 17
    + Tab 18 can render without re-loading each round's payload."""
    rounds_path = REPO / "archive" / "cube_rounds" / "rounds.json"
    if not rounds_path.exists():
        return {"rounds": [], "cell_compare": []}
    try:
        registry = json.loads(rounds_path.read_text(encoding="utf-8"))
    except Exception:
        return {"rounds": [], "cell_compare": []}
    rounds = registry.get("rounds", [])

    # For Tab 18: build a per-(strategy, exit_method) row containing
    # n / sharpe / verdict for every round so a single table shows
    # the cross-round evolution per cell.
    per_round_l2 = {}
    for r in rounds:
        rid = r.get("id", "?")
        path = r.get("exit_method_analysis_path")
        if not path:
            per_round_l2[rid] = {}
            continue
        ema_path = REPO / path
        if not ema_path.exists():
            per_round_l2[rid] = {}
            continue
        try:
            ema = json.loads(ema_path.read_text(encoding="utf-8"))
        except Exception:
            per_round_l2[rid] = {}
            continue
        per_round_l2[rid] = {
            (row["strategy"], row["exit_method"]): row
            for row in ema.get("layer_2_per_strategy_exit_cell", [])
        }

    # Union of all cell keys across all rounds.
    all_keys = set()
    for d in per_round_l2.values():
        all_keys.update(d.keys())

    cell_compare = []
    round_ids = [r.get("id", "?") for r in rounds]
    for k in sorted(all_keys):
        strat, em = k
        row = {"strategy": strat, "exit_method": em}
        for rid in round_ids:
            cell = per_round_l2.get(rid, {}).get(k)
            row[f"{rid}_n"] = cell.get("n") if cell else None
            row[f"{rid}_sharpe"] = cell.get("sharpe") if cell else None
            row[f"{rid}_verdict"] = cell.get("verdict") if cell else None
        # Convenience delta R3 vs R2 if both present.
        if "R2" in round_ids and "R3" in round_ids:
            s2 = row.get("R2_sharpe")
            s3 = row.get("R3_sharpe")
            if s2 is not None and s3 is not None:
                row["sharpe_delta_R3_R2"] = round(s3 - s2, 4)
            else:
                row["sharpe_delta_R3_R2"] = None
        cell_compare.append(row)
    # Sort by absolute Sharpe delta DESC so the most-changed cells
    # bubble to the top of Tab 18.
    cell_compare.sort(
        key=lambda r: -abs(r.get("sharpe_delta_R3_R2") or 0))

    return {
        "rounds":       rounds,
        "round_ids":    round_ids,
        "current_round": round_ids[-1] if round_ids else None,
        "cell_compare": cell_compare,
    }


def compute_cube_diff(current_opt: dict, current_out_dir: Path) -> dict:
    """Batch 441 (2026-05-29): per-cell + per-bucket + trade-count delta
    between the current cube run and the prior snapshot. Used by Tab 16.

    Looks for prior snapshot files at:
      archive/<latest-date>-pre-rerun-cube-snapshot/exit_method_analysis_prior.json
      archive/<latest-date>-pre-rerun-cube-snapshot/producer_zero_post_cube_audit_prior.json
      archive/<latest-date>-pre-rerun-cube-snapshot/trade_log_prior.csv

    Returns {} if no prior snapshot exists - Tab 16 will then render
    the static "diff not yet computed" callout instead of a table.
    """
    # Find newest snapshot dir.
    archive_root = REPO / "archive"
    snapshot_dirs = sorted([d for d in archive_root.glob("*-pre-rerun-cube-snapshot")
                            if d.is_dir()])
    if not snapshot_dirs:
        return {}
    snap = snapshot_dirs[-1]
    prior_ema_path = snap / "exit_method_analysis_prior.json"
    prior_pza_path = snap / "producer_zero_post_cube_audit_prior.json"
    prior_log_path = snap / "trade_log_prior.csv"
    if not prior_ema_path.exists():
        return {}
    # Load prior + current.
    try:
        prior_ema = json.loads(prior_ema_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    current_ema = current_opt.get("exit_method_analysis") or {}
    prior_l2 = {(r["strategy"], r["exit_method"]): r
                for r in prior_ema.get("layer_2_per_strategy_exit_cell", [])}
    current_l2 = {(r["strategy"], r["exit_method"]): r
                  for r in current_ema.get("layer_2_per_strategy_exit_cell", [])}
    prior_keys = set(prior_l2)
    current_keys = set(current_l2)

    # Per-cell deltas (intersect).
    cells_improved = []
    cells_regressed = []
    verdict_upgrades = 0
    verdict_downgrades = 0
    VERDICT_RANK = {"FAIL": 0, "INSUFFICIENT_SAMPLE": 0,
                    "PASS": 1, "PASS-strict": 2}
    for k in prior_keys & current_keys:
        p, c = prior_l2[k], current_l2[k]
        delta = {
            "strategy":      k[0],
            "exit_method":   k[1],
            "n_prior":       p.get("n"),
            "n_current":     c.get("n"),
            "sharpe_prior":  p.get("sharpe"),
            "sharpe_current": c.get("sharpe"),
            "sharpe_delta":  ((c.get("sharpe") or 0) - (p.get("sharpe") or 0)),
            "verdict_prior":   p.get("verdict"),
            "verdict_current": c.get("verdict"),
        }
        if delta["sharpe_delta"] > 0:
            cells_improved.append(delta)
        elif delta["sharpe_delta"] < 0:
            cells_regressed.append(delta)
        pv = VERDICT_RANK.get(p.get("verdict", "FAIL"), 0)
        cv = VERDICT_RANK.get(c.get("verdict", "FAIL"), 0)
        if cv > pv:
            verdict_upgrades += 1
        elif cv < pv:
            verdict_downgrades += 1
    cells_improved.sort(key=lambda r: -r["sharpe_delta"])
    cells_regressed.sort(key=lambda r: r["sharpe_delta"])

    # Bucket diff.
    bucket_diff = {}
    try:
        prior_pza = json.loads(prior_pza_path.read_text(encoding="utf-8")) if prior_pza_path.exists() else {}
    except Exception:
        prior_pza = {}
    current_pza = current_opt.get("producer_zero_audit") or {}
    for bucket in ("PRODUCER_LAYER_ZERO_LIKELY",
                   "COMPOUND_RESTRICTIVE", "SKIPPED_AT_ENGINE"):
        prior_n = (prior_pza.get("summary") or {}).get(bucket)
        current_n = (current_pza.get("summary") or {}).get(bucket)
        if prior_n is not None or current_n is not None:
            bucket_diff[bucket] = {
                "prior":   prior_n,
                "current": current_n,
                "delta":   (current_n or 0) - (prior_n or 0)
                           if prior_n is not None and current_n is not None
                           else None,
            }

    # Total trade count.
    def _count_csv_rows(p: Path) -> int | None:
        if not p.exists():
            return None
        try:
            with p.open("r", encoding="utf-8") as fh:
                return sum(1 for _ in fh) - 1
        except Exception:
            return None

    total_trades_prior = _count_csv_rows(prior_log_path)
    total_trades_current = _count_csv_rows(current_out_dir / "trade_log.csv")

    return {
        "snapshot_dir":              str(snap.relative_to(REPO)),
        "total_trades_prior":        total_trades_prior,
        "total_trades_current":      total_trades_current,
        "total_trades_delta":        (
            (total_trades_current or 0) - (total_trades_prior or 0)
            if total_trades_prior is not None and total_trades_current is not None
            else None),
        "cells_prior":               len(prior_keys),
        "cells_current":             len(current_keys),
        "cells_new":                 len(current_keys - prior_keys),
        "cells_retired":             len(prior_keys - current_keys),
        "cells_improved":            len(cells_improved),
        "cells_regressed":           len(cells_regressed),
        "verdict_upgrades":          verdict_upgrades,
        "verdict_downgrades":        verdict_downgrades,
        "bucket_diff":               bucket_diff,
        "cells_improved_top20":      cells_improved[:20],
        "cells_regressed_top20":     cells_regressed[:20],
    }


def load_optimizer_dir() -> dict:
    """Batch 419: aggregate cube-optimizer outputs into 4 payload sections
    consumed by the 4 new dashboard tabs (Optimizer Summary / Candidates /
    Quiet Strategies / Cell Verdict Cube).

    Returns empty sections when OPT_DIR is missing - tabs render as "no
    data" gracefully. Per locked workflow Stage 3 expectations doc.
    """
    out = {
        "optimizer_summary_md": "",
        "per_strategy_candidates": {},
        "exit_method_analysis": {},
        "producer_zero_audit": {},
        "optimizer_dir": (
            str(OPT_DIR.relative_to(REPO)) if OPT_DIR.exists() and OPT_DIR.is_relative_to(REPO)
            else (str(OPT_DIR) if OPT_DIR.exists() else None)
        ),
    }
    if not OPT_DIR.exists():
        return out
    # optimization_summary.md (top of file only; script-generated)
    md = OPT_DIR / "optimization_summary.md"
    if md.exists():
        try:
            out["optimizer_summary_md"] = md.read_text(encoding="utf-8")
        except Exception:
            pass
    # exit_method_analysis.json (Lens B L1+L2+L3)
    ema = OPT_DIR / "exit_method_analysis.json"
    if ema.exists():
        try:
            out["exit_method_analysis"] = json.loads(
                ema.read_text(encoding="utf-8"))
        except Exception:
            pass
    # producer_zero_post_cube_audit.json (3-bucket quiet classification)
    pza = OPT_DIR / "producer_zero_post_cube_audit.json"
    if pza.exists():
        try:
            out["producer_zero_audit"] = json.loads(
                pza.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Per-strategy JSONs (~85-100 files; one per fired strategy)
    skip = {"exit_method_analysis.json", "producer_zero_post_cube_audit.json"}
    for f in OPT_DIR.glob("*.json"):
        if f.name in skip:
            continue
        try:
            out["per_strategy_candidates"][f.stem] = json.loads(
                f.read_text(encoding="utf-8"))
        except Exception:
            continue
    return out


def load_parquet(name: str, head: int | None = None) -> list[dict]:
    p = OUT_DIR / name
    if not p.exists():
        return []
    try:
        df = pd.read_parquet(p)
    except Exception:
        return []
    if head is not None:
        df = df.head(head)
    # Date typing -> ISO string for JS
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d")
        elif df[col].dtype == "object":
            df[col] = df[col].astype(str).where(df[col].notna(), None)
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def build() -> dict:
    # ---- Tab 1: per-strategy ranking ----
    backtest_results = load_csv("backtest_results.csv")
    winning = load_json("winning_strategies.json") or {}

    # ---- Tab 2: regime heatmap (per-strategy x regime verdicts) ----
    regime_matrix = load_json("strategy_regime_matrix.json") or {}
    regime_summary = load_json("regime_stratified_summary.json") or {}

    # ---- Tab 3: MAE / MFE distribution ----
    mae_bucket = load_csv("exit_by_mae_bucket.csv")
    mfe_bucket = load_csv("exit_by_mfe_bucket.csv")

    # ---- Tab 4: equity curve ----
    equity = load_parquet("equity_curve.parquet")
    portfolio_summary = load_json("portfolio_summary.json") or {}
    portfolio_metrics = load_json("portfolio_metrics.json") or {}

    # ---- Tab 5: walk-forward + improvements ----
    improvements = load_json("improvements_summary.json") or {}
    rolling_sharpe = load_json("rolling_sharpe_stability.json") or {}
    bootstrap_ci = load_csv("bootstrap_ci.csv")
    stress = load_json("stress_metrics.json") or {}

    # ---- Tab 6: smart money lift ----
    smart_money = load_csv("exit_by_smart_money_signal_present.csv")
    congressional = load_csv("congressional_correlation.csv")

    # ---- Tab 7: sector breakdown ----
    by_sector = load_csv("exit_by_sector.csv")
    sector_conc = load_csv("sector_concentration.csv")

    # ---- Tab 8: skipped trades ----
    skipped = load_csv("skipped_trades.csv", head=5000)

    # ---- Tab 9: circuit breaker log ----
    cb_log = load_csv("circuit_breaker_log.csv")
    cb_by_active = load_csv("exit_by_circuit_breaker_active_during_hold.csv")

    # ---- Trade-level + exit breakdowns (cross-tab) ----
    # Batch 180: fall back to CSV if parquet missing (smoke runs emit CSV-only)
    # Batch 437b (2026-05-29): cube trade_log has wide text columns
    # (signals_at_entry ~10.9 KB/row, context_paragraph, agent_reasoning,
    # context_bullets, fail_reason). 10000 rows -> 109+ MB of just one
    # column blew the 100 MB GitHub file cap. Reduce preview head to
    # 1000 + drop the wide blob columns so the dashboard table stays
    # under a few MB.
    _PREVIEW_HEAD = 1000
    _DROP_COLS = ["signals_at_entry", "context_paragraph",
                  "agent_reasoning", "context_bullets", "fail_reason"]
    trade_log = (load_parquet("trade_log.parquet", head=_PREVIEW_HEAD)
                 or load_csv("trade_log.csv", head=_PREVIEW_HEAD))
    if trade_log:
        for row in trade_log:
            for c in _DROP_COLS:
                row.pop(c, None)
    exit_methods = load_csv("exit_method_multi_dim_cube.csv")
    exit_best = load_csv("exit_strategy_best.csv")
    exit_comparison = load_csv("exit_strategy_comparison.csv")

    # ---- Per-dimension exit breakdowns (extra optional tabs) ----
    # Batch 437b: cap each breakdown at 200 rows. Cube outputs are
    # large (4625 cells x N regimes); 20 of them at full size totalled
    # ~230 MB. Owner can drill into a specific breakdown via the cube
    # tabs if needed.
    _BREAKDOWN_HEAD = 200
    other_breakdowns: dict[str, list] = {}
    for csv in OUT_DIR.glob("exit_by_*.csv"):
        # Skip the ones already used in dedicated tabs
        if csv.name in (
            "exit_by_mae_bucket.csv", "exit_by_mfe_bucket.csv",
            "exit_by_smart_money_signal_present.csv", "exit_by_sector.csv",
            "exit_by_circuit_breaker_active_during_hold.csv",
        ):
            continue
        other_breakdowns[csv.stem.replace("exit_by_", "")] = load_csv(
            csv.name, head=_BREAKDOWN_HEAD)

    # ---- Batch 419: cube-optimizer outputs (Tabs 10-13) ----
    opt = load_optimizer_dir()

    # ---- Batch 441 (2026-05-29): Cube Diff (Tab 16) ----
    cube_diff = compute_cube_diff(opt, OUT_DIR)

    # ---- Batch 443 (2026-05-29): Iteration Rounds (Tab 17) +
    #      Cell Cube Comparison (Tab 18) ----
    iter_rounds = load_iteration_rounds()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_dir": (
            str(OUT_DIR.relative_to(REPO)) if OUT_DIR.is_relative_to(REPO)
            else str(OUT_DIR)
        ),
        # Batch 419: optimizer payload sections (4 new tabs)
        "optimizer_dir":            opt["optimizer_dir"],
        "optimizer_summary_md":     opt["optimizer_summary_md"],
        "per_strategy_candidates":  opt["per_strategy_candidates"],
        "exit_method_analysis":     opt["exit_method_analysis"],
        "producer_zero_audit":      opt["producer_zero_audit"],
        # Batch 441: cube iteration diff (Tab 16)
        "cube_diff":                cube_diff,
        # Batch 443: iteration rounds registry (Tab 17) + cross-round
        # cell-level comparison (Tab 18)
        "iteration_rounds":         iter_rounds.get("rounds", []),
        "current_round":            iter_rounds.get("current_round"),
        "round_ids":                iter_rounds.get("round_ids", []),
        "cell_cube_comparison":     iter_rounds.get("cell_compare", []),
        # Tab 1
        "backtest_results": backtest_results,
        "winning_strategies": winning,
        # Tab 2
        "strategy_regime_matrix": regime_matrix,
        "regime_stratified_summary": regime_summary,
        # Tab 3
        "mae_bucket": mae_bucket,
        "mfe_bucket": mfe_bucket,
        # Tab 4
        "equity_curve": equity,
        "portfolio_summary": portfolio_summary,
        "portfolio_metrics": portfolio_metrics,
        # Tab 5
        "improvements_summary": improvements,
        "rolling_sharpe_stability": rolling_sharpe,
        "bootstrap_ci": bootstrap_ci,
        "stress_metrics": stress,
        # Tab 6
        "smart_money_exit": smart_money,
        "congressional_correlation": congressional,
        # Tab 7
        "by_sector": by_sector,
        "sector_concentration": sector_conc,
        # Tab 8
        "skipped_trades": skipped,
        # Tab 9
        "circuit_breaker_log": cb_log,
        "cb_by_active": cb_by_active,
        # Cross-tab
        "trade_log_preview": trade_log,
        "exit_methods": exit_methods,
        "exit_best": exit_best,
        "exit_comparison": exit_comparison,
        "exit_breakdowns": other_breakdowns,
    }


def main() -> int:
    print(f"Phase 1A dashboard build -> {DASH}")
    if not OUT_DIR.exists():
        print(f"ERROR: {OUT_DIR} not found; run backtest first")
        return 1
    payload = build()

    # Plain JSON (audit / consumers)
    (DASH / "data.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    # Browser-loadable JS module
    # Batch 422 (2026-05-28): fix latent dashboard-blank bug. In a regular
    # <script> context (non-module), top-level `const` creates a lexical
    # global but does NOT attach to window. app.js's
    # `const D = window.PHASE_1A_DATA || {}` therefore always saw {} ->
    # all tabs rendered blank. Owner reported "all tabs blank, headers
    # visible" post-Batch-419. Switch to explicit `window.PHASE_1A_DATA = `
    # so the assignment attaches to the global object.
    js = "window.PHASE_1A_DATA = " + json.dumps(payload, default=str) + ";"
    (DASH / "data.js").write_text(js, encoding="utf-8")
    (DASH / "last_run.txt").write_text(payload["generated_at"] + "\n", encoding="utf-8")

    # Summary
    print(f"  generated_at: {payload['generated_at']}")
    print(f"  backtest_results rows:  {len(payload['backtest_results'])}")
    print(f"  trade_log preview rows: {len(payload['trade_log_preview'])}")
    print(f"  equity_curve points:    {len(payload['equity_curve'])}")
    print(f"  skipped_trades rows:    {len(payload['skipped_trades'])}")
    print(f"  exit_breakdowns kinds:  {len(payload['exit_breakdowns'])}")
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
