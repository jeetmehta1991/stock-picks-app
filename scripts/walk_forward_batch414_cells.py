"""Batch 414 Stage 6 walk-forward (DEC-505) at (strategy x exit) CELL level.

Source attribution (per CHECKLIST #77):
  - Cube: output_batch395_final/trade_exit_detail.csv (AWS Phase 1A-beta merge)
  - Method: DEC-505 4-fold expanding-window, disjoint 1y OOS
  - Owner directive 2026-05-28: validate the 9 Batch 414 STRATEGY_EXIT_OVERRIDE
    winners pre-Phase-1B-alpha agent budget commit ("Owner gate at 1A-alpha
    (rules-only Sharpe >= 0.7 OOS) before $300 1B-alpha budget commits"
    per CLAUDE.md).

Why this script exists (cell vs strategy):
  output_batch395_final/walk_forward_validation.csv is STRATEGY-level
  (aggregated across all 25 exits at cube-run time). The Batch 414 winners
  use breakeven_plus_trail specifically; this script slices the cube
  trade_exit_detail.csv to (strategy x breakeven_plus_trail) cells and
  computes per-cell, per-fold IS/OOS Sharpe.

Output:
  output_batch395_final/walk_forward_batch414_cells.json
  Per-strategy, per-fold IS + OOS dict with n, sharpe, win_rate,
  profit_factor, mean_pp.

1A-alpha gate check:
  Per CLAUDE.md owner-gate rule: at least 1 strategy must have OOS Sharpe
  >= 0.7 in at least 1 fold for the $300 Phase 1B-alpha agent overlay
  budget to be eligible to commit. Script prints GATE OPEN / GATE LOCKED
  at the bottom of stdout.

Usage:
  python scripts/walk_forward_batch414_cells.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parent.parent
CUBE_CSV = REPO / "output_batch395_final" / "trade_exit_detail.csv"
OUT_JSON = REPO / "output_batch395_final" / "walk_forward_batch414_cells.json"


# Batch 414 winners (canonical source: backtest/config.py STRATEGY_EXIT_OVERRIDE
# entries marked "Batch 414"). Hard-coded here to keep the script self-contained
# and avoid coupling to a config import that may drift.
BATCH_414_WINNERS = [
    "bollinger_tight",
    "xs_momentum_top_decile",
    "cmf_flip",
    "monthly_bias_momentum_long",
    "xs_quality_top_quintile_long",
    "pead_long",
    "pairs_mean_reversion_long",
    "adx_initiation",
    "xs_low_beta_long",
]
WINNING_EXIT = "breakeven_plus_trail"


# DEC-505 4-fold expanding-window, disjoint 1y OOS.
# Warmup 1y: 2021-05-05 -> 2022-05-05 (training only; not OOS-tested)
FOLDS = [
    ("fold_1", date(2021, 5, 5), date(2022, 5, 5),
                date(2022, 5, 5), date(2023, 5, 5)),
    ("fold_2", date(2021, 5, 5), date(2023, 5, 5),
                date(2023, 5, 5), date(2024, 5, 5)),
    ("fold_3", date(2021, 5, 5), date(2024, 5, 5),
                date(2024, 5, 5), date(2025, 5, 5)),
    ("fold_4", date(2021, 5, 5), date(2025, 5, 5),
                date(2025, 5, 5), date(2026, 5, 5)),
]


def _cell_stats(pnl: pd.Series):
    n = len(pnl)
    if n < 5:
        return None
    arr = pnl.values
    mean_pp = float(arr.mean())
    std_pp = float(arr.std(ddof=1)) if n > 1 else 0.0
    sharpe = mean_pp / std_pp if std_pp > 0 else 0.0
    wins = float(arr[arr > 0].sum())
    losses = float(abs(arr[arr < 0].sum()))
    pf = wins / losses if losses > 0 else 999.0
    wr = float((arr > 0).mean())
    return {
        "n":       n,
        "sharpe":  round(sharpe, 3),
        "wr":      round(wr, 3),
        "pf":      round(pf, 2),
        "mean_pp": round(mean_pp, 3),
    }


def main() -> int:
    if not CUBE_CSV.exists():
        print(f"[ERROR] {CUBE_CSV} not found; run AWS merge first")
        return 1

    print(f"reading {CUBE_CSV.name} (filter to 9 winners x {WINNING_EXIT})...")
    cube = pd.read_csv(
        CUBE_CSV,
        usecols=["strategy", "exit_method", "entry_date", "pnl_pct",
                  "hold_days"],
    )
    cube = cube[
        (cube["strategy"].isin(BATCH_414_WINNERS))
        & (cube["exit_method"] == WINNING_EXIT)
    ]
    cube["entry_date"] = pd.to_datetime(cube["entry_date"]).dt.date
    print(f"filtered rows: {len(cube)}")
    print()

    print(f'{"strategy":<32} {"fold":<7} {"phase":<5} {"n":>6} '
          f'{"sharpe":>7} {"wr":>6} {"pf":>6}  gate')
    print("-" * 110)
    results = {}
    for strat in BATCH_414_WINNERS:
        sub = cube[cube["strategy"] == strat]
        if sub.empty:
            continue
        results[strat] = {}
        for fold_name, is_start, is_end, oos_start, oos_end in FOLDS:
            is_mask = (sub["entry_date"] >= is_start) \
                & (sub["entry_date"] < is_end)
            oos_mask = (sub["entry_date"] >= oos_start) \
                & (sub["entry_date"] < oos_end)
            is_stats = _cell_stats(sub.loc[is_mask, "pnl_pct"])
            oos_stats = _cell_stats(sub.loc[oos_mask, "pnl_pct"])
            results[strat][fold_name] = {"is": is_stats, "oos": oos_stats}
            if is_stats:
                print(f'{strat:<32} {fold_name:<7} {"IS":<5} '
                      f'{is_stats["n"]:>6} {is_stats["sharpe"]:>7} '
                      f'{is_stats["wr"]:>6} {is_stats["pf"]:>6}')
            if oos_stats:
                sh = oos_stats["sharpe"]
                gate = "PASS" if sh >= 0.7 else ("CLOSE" if sh >= 0.5
                                                  else "FAIL")
                print(f'{strat:<32} {fold_name:<7} {"OOS":<5} '
                      f'{oos_stats["n"]:>6} {oos_stats["sharpe"]:>7} '
                      f'{oos_stats["wr"]:>6} {oos_stats["pf"]:>6}  {gate}')
            else:
                print(f'{strat:<32} {fold_name:<7} {"OOS":<5} '
                      f'{"<5":>6}')
        print()

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"saved -> {OUT_JSON}")

    # 1A-alpha gate check
    print()
    print("=== 1A-alpha gate (CLAUDE.md owner gate: "
          "Sharpe >= 0.7 OOS in any fold) ===")
    gate_open = False
    for strat in BATCH_414_WINNERS:
        if strat not in results:
            continue
        oos_sharpes = []
        for fold_name, _, _, _, _ in FOLDS:
            oos_stats = results[strat][fold_name]["oos"]
            if oos_stats:
                oos_sharpes.append(oos_stats["sharpe"])
        if not oos_sharpes:
            print(f"  {strat:<32} no OOS folds with n>=5")
            continue
        max_oos = max(oos_sharpes)
        pass_gate = max_oos >= 0.7
        if pass_gate:
            gate_open = True
        status = "PASS" if pass_gate else (
            "CLOSE" if max_oos >= 0.5 else "FAIL")
        print(f"  {strat:<32} max OOS Sharpe across 4 folds = "
              f"{max_oos:.3f}  {status}")
    print()
    print(f"1A-alpha gate: {'OPEN' if gate_open else 'LOCKED'}")
    return 0 if gate_open else 2


if __name__ == "__main__":
    import sys
    sys.exit(main())
