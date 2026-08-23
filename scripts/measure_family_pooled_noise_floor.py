#!/usr/bin/env python
"""Noise floor for a FAMILY-POOLED EMA-axis measurement (B2068, council S6-B2006b step d).

THE QUESTION (the B2065 council's "one thing to do first"): the measured
selection-noise floor of 0.333 Sharpe (B2009, cell-grain twin gaps in
output_audit/b1467_exit_selection_noise.json) is DESIGN-CONDITIONAL - it was
measured for per-cell best-of-26 exit selection at per-cell trade counts. A
family-pooled EMA-axis measurement grades one config on trades pooled across
the ~114 compute_ema_sma consumers, so its floor must be recomputed at the
pooled grain BEFORE any run shape is chosen. Offline, $0, from the existing
R5 cube.

METHOD - the same statistic generalized, two components:

  replication floor(N)   median |Sharpe(A) - Sharpe(B)| over R independent
                         bootstrap pairs A,B of N trades each, drawn from the
                         same pooled population. This is the B1467 twin-gap
                         statistic with the trade population held fixed and
                         measurement repeated - pure replication noise at
                         size N.
  selection lift(N, K)   mean(max over K arms of Sharpe_k) - pooled Sharpe,
                         K independent N-samples under the NULL (all arms one
                         population). The optimism a best-of-K pick carries
                         at size N - the family sweep's analog of best-of-26
                         exit selection.

Sharpe is roster_core's own annualized per-trade _sharpe (ONE definition,
L561); trades are the IS WINDOW ONLY (holdout stays sealed - this measures
noise, and reading holdout for it would spend the read-once budget), at ONE
exit per trade (atr_trail_1x, the production default) so no trade appears 26x.

CONTROL (L588 - the control takes the same path): the floor is also computed
at the observed per-cell median n. The B2009 twin statistic at that grain
also contains exit-selection disagreement, so the expectation is same ORDER
as 0.333, not equality.

Bootstrap on REAL trades from output_r5_merged_1_7/trade_exit_detail.csv,
seed 2068 - resampled measurements of real data, not synthetic values.

Output: output_audit/b2068_family_pooled_noise_floor.json + printed table.
HAND-RUN:  PYTHONPATH=. python scripts/measure_family_pooled_noise_floor.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from roster_core import COST_BPS, IS_END, IS_START, WINSORIZE, _sharpe  # noqa: E402

CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
FAMILY_MAP = ROOT / "output_audit" / "strategy_producer_map.csv"
OUT = ROOT / "output_audit" / "b2068_family_pooled_noise_floor.json"
EXIT = "atr_trail_1x"
SEED = 2068
LADDER = (50, 100, 300, 1000, 3000, 10000, 30000)
KS = (5, 20)
R_PAIRS = 400
R_SEL = 200
# named references the floor is read against (sources in the JSON):
REFERENCES = {
    "cell_grain_floor_b2009": 0.333,
    "roster_margin_52w_high_b2014": 0.281,
    "roster_margin_xs_momentum_b2014": 0.624,
    "ten_pct_of_sharpe_gate": 0.1,
}


def family_members() -> list[str]:
    with FAMILY_MAP.open(encoding="utf-8") as f:
        return sorted({r["strategy"] for r in csv.DictReader(f)
                       if r["producer"] == "compute_ema_sma"})


def _boot_sharpe(pnl: np.ndarray, hold: np.ndarray, idx: np.ndarray) -> float | None:
    s = _sharpe(pnl[idx], hold[idx], min_n=10)
    return None if s is None else s["sharpe"]


def replication_floor(pnl: np.ndarray, hold: np.ndarray, n: int,
                      rng: np.random.Generator, r_pairs: int = R_PAIRS) -> float:
    """median |dSharpe| between paired independent bootstrap N-samples."""
    gaps = []
    for _ in range(r_pairs):
        a = _boot_sharpe(pnl, hold, rng.integers(0, len(pnl), n))
        b = _boot_sharpe(pnl, hold, rng.integers(0, len(pnl), n))
        if a is not None and b is not None:
            gaps.append(abs(a - b))
    return float(np.median(gaps)) if gaps else float("nan")


def selection_lift(pnl: np.ndarray, hold: np.ndarray, n: int, k: int,
                   rng: np.random.Generator, r_sel: int = R_SEL) -> float:
    """mean(best-of-K bootstrap Sharpe) - population Sharpe, under the null."""
    pop = _sharpe(pnl, hold, min_n=10)
    pop_sh = pop["sharpe"] if pop else 0.0
    lifts = []
    for _ in range(r_sel):
        arms = [_boot_sharpe(pnl, hold, rng.integers(0, len(pnl), n))
                for _ in range(k)]
        arms = [a for a in arms if a is not None]
        if arms:
            lifts.append(max(arms) - pop_sh)
    return float(np.mean(lifts)) if lifts else float("nan")


def required_n(floors: dict[int, float], bar: float) -> int | None:
    """smallest ladder N whose measured floor is at or below the bar."""
    for n in sorted(floors):
        if floors[n] <= bar:
            return n
    return None


def block_replication_floor(pnl: np.ndarray, hold: np.ndarray,
                            day_idx: list[np.ndarray], n_days: int,
                            rng: np.random.Generator,
                            r_pairs: int = R_PAIRS) -> float:
    """B2080 (design gate 4): the CORRELATION-AWARE floor. Family members
    share entry days, so iid trade-resampling overstates effective N; this
    resamples ENTRY DAYS with replacement (each day carries ALL its trades
    together), preserving the within-day cross-strategy correlation. The
    median |dSharpe| between paired independent day-resamples of `n_days`
    days is the replication floor at that day-count."""
    gaps = []
    n = len(day_idx)
    for _ in range(r_pairs):
        pair = []
        for _arm in range(2):
            take = rng.integers(0, n, n_days)
            idx = np.concatenate([day_idx[i] for i in take])
            s = _sharpe(pnl[idx], hold[idx], min_n=10)
            pair.append(None if s is None else s["sharpe"])
        if pair[0] is not None and pair[1] is not None:
            gaps.append(abs(pair[0] - pair[1]))
    return float(np.median(gaps)) if gaps else float("nan")


def main() -> int:
    import pandas as pd
    fam = family_members()
    print(f"EMA family: {len(fam)} strategies (producer compute_ema_sma, "
          f"per {FAMILY_MAP.name})")
    df = pd.read_csv(CUBE, usecols=["strategy", "direction", "exit_method",
                                    "entry_date", "pnl_pct", "hold_days"],
                     dtype={"strategy": "category", "direction": "category",
                            "exit_method": "category",
                            "pnl_pct": "float32", "hold_days": "float32"})
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    df = df[(df.exit_method == EXIT) & df.strategy.isin(fam)
            & (df.entry_date >= IS_START) & (df.entry_date < IS_END)]
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0
    pnl = df["pnl_pct"].to_numpy(dtype=np.float64)
    hold = df["hold_days"].to_numpy(dtype=np.float64)
    n_pool = len(pnl)
    cell_n = df.groupby("strategy", observed=True).size()
    cell_n = cell_n[cell_n > 0]
    med_cell = int(cell_n.median())
    pop = _sharpe(pnl, hold, min_n=10)
    print(f"pooled IS trades at exit={EXIT}: {n_pool:,} across "
          f"{cell_n.shape[0]} strategies with fires "
          f"(median per-strategy cell n = {med_cell}); "
          f"pooled Sharpe {pop['sharpe'] if pop else None}")

    rng = np.random.default_rng(SEED)
    ladder = sorted(set([n for n in LADDER if n < n_pool] + [med_cell, n_pool]))
    floors, sel = {}, {}
    print(f"\n{'N':>8} | {'replication floor':>17} | "
          + " | ".join(f"best-of-{k} lift" for k in KS))
    for n in ladder:
        floors[n] = round(replication_floor(pnl, hold, n, rng), 4)
        sel[n] = {k: round(selection_lift(pnl, hold, n, k, rng), 4) for k in KS}
        tag = " <- per-cell grain (control)" if n == med_cell else (
              " <- full pool" if n == n_pool else "")
        print(f"{n:>8} | {floors[n]:>17} | "
              + " | ".join(f"{sel[n][k]:>14}" for k in KS) + tag)

    req = {name: required_n(floors, bar) for name, bar in REFERENCES.items()}
    print("\nrequired pooled N for the replication floor to reach each reference:")
    for name, bar in REFERENCES.items():
        print(f"  {name} ({bar}): N >= {req[name]}")

    # B2080 (design gate 4): the correlation-aware floors, same ladder,
    # expressed in DAYS carrying ~the ladder's trade counts on average.
    dser = df.groupby("entry_date", observed=True).indices
    days = sorted(dser)
    day_idx = [np.asarray(dser[d], dtype=np.int64) for d in days]
    tpd = n_pool / len(day_idx)
    print(f"\nBLOCK bootstrap (entry-day resampling): {len(day_idx)} unique "
          f"IS entry-days, mean {tpd:.1f} pooled trades/day")
    block = {}
    for n in ladder:
        nd = max(5, int(round(n / tpd)))
        if nd > len(day_idx):
            nd = len(day_idx)
        block[n] = round(block_replication_floor(pnl, hold, day_idx, nd, rng), 4)
        print(f"{n:>8} trades ~ {nd:>4} days | block floor {block[n]:>7} "
              f"(iid was {floors[n]})")
    req_block = {name: required_n(block, bar) for name, bar in REFERENCES.items()}
    print("required pooled N (BLOCK floor) per reference:")
    for name, bar in REFERENCES.items():
        print(f"  {name} ({bar}): N >= {req_block[name]}")

    OUT.write_text(json.dumps({
        "cube": str(CUBE.relative_to(ROOT)), "exit": EXIT, "seed": SEED,
        "is_window": [str(IS_START), str(IS_END)],
        "family_size": len(fam), "strategies_with_fires": int(cell_n.shape[0]),
        "pooled_n": n_pool, "median_cell_n": med_cell,
        "pooled_sharpe": pop["sharpe"] if pop else None,
        "replication_floor_by_n": floors,
        "selection_lift_by_n_k": {str(n): sel[n] for n in ladder},
        "block_replication_floor_by_n": block,
        "block_unique_days": len(day_idx),
        "block_mean_trades_per_day": round(tpd, 2),
        "required_n_block": req_block,
        "references": REFERENCES, "required_n": req,
        "r_pairs": R_PAIRS, "r_sel": R_SEL,
    }, indent=1), encoding="utf-8")
    print(f"\n[OK] wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
