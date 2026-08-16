"""scripts/roster_core.py (B1463, ticket S6-B1452a) -- ONE implementation of the window
discipline, the gate evaluation, and the exit-selection objective.

WHY THIS EXISTS
Two scripts independently implemented the same IS-select / holdout-grade discipline:
`build_phase_1b_roster.py` (the canonical roster) and `best_exit_by_gates.py` (the
gates-cleared objective). They duplicated the fold boundaries, the winsorisation, the cost
assumption, the power floor and the five live gates. That duplication is not a tidiness
problem -- it is the B1452 lookahead waiting to happen a second time: if one file's IS_END
drifts, or one starts reading the holdout during selection, nothing detects the divergence
and both keep printing plausible numbers.

S6-OPT-196 will regrade the 196-strategy backlog repeatedly. Two divergent implementations
compound on every regrade, so this is consolidated BEFORE that programme starts, not after.

WHAT IS SHARED HERE
  * fold boundaries          IS 2022-05-05..2025-05-05, HOLDOUT 2025-05-05..2026-05-05
  * return conditioning      winsorise +/-300%, subtract 20bps round-trip
  * power floor              n >= 30 to evaluate at all
  * the five LIVE gates      and the four DEMOTED diagnostics
  * evaluate()               one gate computation
  * select_exit()            IS-only selection with a switchable objective

THE OBJECTIVE SWITCH replaces the fork that justified two files:
  "gates"  argmax IS gates-cleared, tie-break IS Sharpe   (owner directive 2026-08-04)
  "sharpe" argmax IS Sharpe                                (the pre-B1451 objective)
Both read ONLY the in-sample folds. The holdout is graded once, by the caller, on the single
chosen exit. Any function here that touches holdout data during selection is a bug.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from backtest.config import PASSING_CRITERIA as PC          # noqa: E402
from backtest.results.metrics import _sortino_ratio, _deflated_sharpe  # noqa: E402
from walk_forward_r5_cells import _sharpe                    # noqa: E402

# ---- the window discipline: ONE definition -------------------------------------------
IS_START, IS_END = date(2022, 5, 5), date(2025, 5, 5)
HO_START, HO_END = date(2025, 5, 5), date(2026, 5, 5)
WINSORIZE, COST_BPS, MIN_N, FDR_Q, JACCARD = 300.0, 20.0, 30, 0.05, 0.70

LIVE_GATES = ("pooled_sharpe", "profit_factor", "sortino", "psr",
              "min_trades_holdout", "min_trades_full_period")   # B1496: 5 -> 6
DEMOTED = ("max_drawdown", "calmar", "deflated_sharpe", "win_rate")

CUBE_COLUMNS = ["strategy", "direction", "exit_method", "entry_date",
                "ticker", "pnl_pct", "hold_days"]
CUBE_DTYPES = {"strategy": "category", "direction": "category", "exit_method": "category",
               "ticker": "category", "pnl_pct": "float32", "hold_days": "float32"}


# B1602 (owner-approved option 2, L467/CHECKLIST #193): exits that DEGRADED to a
# different exit in every cube produced before B1593. Relabelling downstream was
# reverted by the next regeneration, so the correction lives HERE - in the shared
# library every consumer imports - and therefore survives.
#
# `regime_flip` : no caller ever passed `regime_series`, so it fell back to a
#   20-day time stop on every trade in every cube (measured identical to
#   time_stop_20d on 330/330). B1593 fix C wired it, so cubes generated AFTER
#   that fix are genuine and must NOT be relabelled.
DEGRADED_EXITS_PRE_B1593 = {"regime_flip": "time_stop_20d"}


def truthful_exit_name(exit_name, cube_predates_b1593=True):
    """Report what an exit ACTUALLY DID, not what it was called.

    Returns (label, footnote). A cube generated after B1593 is returned
    unchanged - the degradation was fixed, not permanent.
    """
    if not cube_predates_b1593:
        return exit_name, ""
    true_name = DEGRADED_EXITS_PRE_B1593.get(str(exit_name))
    if not true_name:
        return exit_name, ""
    return true_name, (f"[was labelled `{exit_name}`; it DEGRADED to "
                       f"`{true_name}` in every pre-B1593 cube - L461]")


def load_cube(path: Path, extra_columns: list[str] | None = None) -> pd.DataFrame:
    """Read a cube with the shared conditioning applied exactly once.

    Categorical labels + float32 keep peak RSS ~4x lower, so regenerating does not depend
    on the machine being otherwise idle (B1455b OOM).
    """
    cols = list(CUBE_COLUMNS) + list(extra_columns or [])
    dtypes = dict(CUBE_DTYPES)
    for c in (extra_columns or []):
        dtypes.setdefault(c, "category")
    df = pd.read_csv(path, usecols=cols, low_memory=False, dtype=dtypes)
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0
    return df


def evaluate(pnl: pd.Series, hold: pd.Series, *, min_n: int | None = None,
             pf_bar: float | None = None, full_period_n: int | None = None) -> dict | None:
    """The five live gates on one (cell, window). None below the power floor.

    `min_n` / `pf_bar` default to the POOLED tier. Callers measuring the per-regime tier
    (criterion #11) pass min_trades_per_regime / min_profit_factor instead -- the tier is
    always the CALLER's explicit choice, never an accident of which constant was in scope
    (L290: the live gate set silently mixed tiers).
    """
    min_n = MIN_N if min_n is None else min_n
    pf_bar = PC["min_profit_factor_overall"] if pf_bar is None else pf_bar
    n = len(pnl)
    if n < min_n:
        return None
    sh = _sharpe(pnl.values, hold)
    sharpe = sh["sharpe"] if sh else None
    sortino = _sortino_ratio(pnl, hold)
    dsr = _deflated_sharpe(sharpe or 0.0, n, float(pnl.skew()), float(pnl.kurtosis()))
    w, l = pnl[pnl > 0], pnl[pnl <= 0]
    pf = float(w.sum() / abs(l.sum())) if len(l) and l.sum() != 0 else float("inf")
    payoff = float(w.mean() / abs(l.mean())) if len(w) and len(l) and l.mean() != 0 else None
    gates = {
        # B1496 (owner-directed rename): was "sharpe_per_regime", a MISNOMER - this computes
        # ONE POOLED Sharpe over the window, with no regime split anywhere. The old name
        # recorded the config key it used to borrow, not the method, and it propagated a false
        # premise to the owner more than once (L287). Now named for what it computes.
        "pooled_sharpe":     sharpe is not None and sharpe >= PC["min_sharpe_overall"],
        "profit_factor":     pf >= pf_bar,
        "sortino":           sortino is not None and sortino >= PC["min_sortino_per_regime"],
        "psr":               dsr.get("psr") is not None and dsr["psr"] >= PC["min_psr"],
        # B1496 (owner-directed split): min_trades is TWO independent requirements and was
        # reported as one gate, understating the gate count and hiding which leg blocks a cell.
        "min_trades_holdout":     n >= PC["min_trades_holdout"],
        "min_trades_full_period": (full_period_n is None
                                   or full_period_n > PC["min_trades_full_period"]),
    }
    return {"n": n, "sharpe": sharpe, "sortino": sortino, "psr": dsr.get("psr"),
            "profit_factor": round(pf, 3), "payoff": round(payoff, 2) if payoff else None,
            "expectancy": round(float(pnl.mean()), 4),
            "win_rate": round(float((pnl > 0).mean()), 3),
            "p": sh.get("p") if sh else None, "ci_lo": sh.get("ci_lo") if sh else None,
            "gates": gates, "n_gates": sum(1 for v in gates.values() if v),
            "all_live_gates": all(gates.values())}


def in_sample(g: pd.DataFrame) -> pd.DataFrame:
    return g[(g.entry_date >= IS_START) & (g.entry_date < IS_END)]


def holdout(g: pd.DataFrame) -> pd.DataFrame:
    return g[(g.entry_date >= HO_START) & (g.entry_date < HO_END)]


def select_exit(g: pd.DataFrame, objective: str = "gates",
                min_n: int | None = None) -> tuple[str | None, dict | None]:
    """Choose ONE exit using IN-SAMPLE data only. Returns (exit_method, its IS stats).

    selection-justified: `gates` maximises the promotion criterion itself (owner directive
    2026-08-04) with IS Sharpe breaking ties; `sharpe` is the pre-B1451 objective retained
    for comparison. Neither reads the holdout -- that is the property B1452 was retracted
    for violating, and it is enforced here by construction: this function is handed the
    full cell frame and slices `in_sample()` itself.
    """
    if objective not in ("gates", "sharpe"):
        raise ValueError(f"unknown objective {objective!r}; use 'gates' or 'sharpe'")
    isg = in_sample(g)
    # B1593 (owner-approved B): COLLAPSE exits that are byte-identical on this
    # cell before selecting. Several "distinct" exits are documented FALLBACKS -
    # regime_flip degrades to time_stop_20d when no regime series is supplied,
    # and reverse_signal degrades to atr_trail for the 214 strategies absent
    # from the Batch-227a registry. Measured identical on 330 of 330 trades
    # (L460). Selecting "best of 26" across duplicates inflates the apparent
    # breadth of the search and makes the n_gates tie-break arbitrary between
    # columns that are the same column.
    _seen: dict[tuple, str] = {}
    _dupes: dict[str, str] = {}
    for _ex, _ge in isg.groupby("exit_method", observed=True):
        _sig = tuple(_ge.sort_values(["ticker", "entry_date"])["pnl_pct"]
                     .round(6).tolist())
        if _sig in _seen:
            _dupes[str(_ex)] = _seen[_sig]
        else:
            _seen[_sig] = str(_ex)
    if _dupes:
        isg = isg[~isg["exit_method"].astype(str).isin(_dupes.keys())]

    best, best_key = None, None
    for ex, ge in isg.groupby("exit_method", observed=True):
        # S6-B1584c: the SEARCH phase passes its own floor. Default None
        # keeps MIN_N, so Phase-2 admission is untouched.
        r = evaluate(ge["pnl_pct"], ge["hold_days"], min_n=min_n)
        if not r:
            continue
        key = ((r["n_gates"], r["sharpe"] or -9) if objective == "gates"
               else (r["sharpe"] or -9,))
        if best_key is None or key > best_key:
            best_key, best = key, (str(ex), r)
    # B1593 (A): disclose what was collapsed so a reader can see the TRUE
    # breadth the selection ran over, rather than assuming 26.
    if best and _dupes:
        best[1]["exits_collapsed"] = len(_dupes)
        best[1]["exits_effective"] = len(_seen)
    return best if best else (None, None)
