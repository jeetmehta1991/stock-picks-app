"""
trigger_followthrough.py
========================

Measures whether a trigger fires at the RIGHT TIME -- i.e. whether, given the
trigger fired, price FOLLOWS THROUGH (the move is real) or REVERSES (the move
was a fakeout) -- and sweeps a threshold to find where that separation is
sharpest, WITHOUT curve-fitting to one sample.

This is the trigger-optimization analog of the fire-count tool and the
gate-redundancy diagnostic. It deliberately does NOT use PnL or any exit/sizing
assumption (those are modeled later). The metric is path-based and exit-free:

    Given the trigger fired on bar t (entry modeled at t+1 open, no lookahead),
    over the next H bars did price reach +TARGET*ATR in the trade direction
    BEFORE it reached -STOP*ATR against it?

  -> a "follow-through" (a barrier-touch race, target-first = success).
  This is the cleanest definition of "entered at the right time" that doesn't
  presuppose an exit rule: a correctly-timed entry is one where the move you
  were trying to catch actually materializes before it invalidates.

KEY DESIGN DECISIONS (each addresses a failure mode seen across the review series)
---------------------------------------------------------------------------------
1. EXIT-FREE metric. Uses an ATR-barrier race, not returns, so the result is
   invariant to the (deferred) exit/sizing model. Optimizing on returns would
   bake in an exit you haven't chosen and would overfit harder.

2. NO-LOOKAHEAD by construction. Entry is t+1 open. The barrier race scans
   t+1 .. t+H using only bars at/after entry. ATR and every trigger parameter
   are computed on data through t (the trigger bar) at the latest.

3. HELD-OUT TIME. Every sweep is fit on a train window and re-measured on a
   disjoint test window. A threshold whose follow-through edge does not persist
   out-of-sample is rejected -- a fakeout filter that only works in-sample is
   not a fakeout filter.

4. PLATEAU not PEAK. The chosen threshold is the centre of the widest stable
   band where train and test agree, NOT the single best train point. A lone
   spike at one grid value is treated as noise.

5. BASE-RATE framing. Every follow-through number is reported against the
   UNFILTERED base rate (all triggers) so you can see whether a parameter adds
   real separation or just shrinks the sample. A filter that raises follow-
   through from 38% to 39% while cutting fires 80% is doing nothing.

6. MULTIPLE-COMPARISON honesty. sweep_threshold returns the full curve, the
   train/test gap, and an n-per-point; the caller is expected to apply the same
   C2 correction used elsewhere before declaring a winner. A convenience
   `is_overfit` flag fires when train and test disagree on the optimum.

INTENDED USE
------------
  - Tune an existing parameter to its separation boundary:
        sweep_threshold(... param sweeps close_top_pct over 0.20..0.50 ...)
    -> tells you 40% is loose and ~28% is the plateau, on held-out data.

  - Decide whether to ADD a new parameter (compression, reclaim-confirm,
    extension) by measuring follow-through WITH vs WITHOUT it, conditional on
    the existing gates already passing (ties to the gate-redundancy diagnostic:
    only add a gate that lifts conditional follow-through).

The module is data-shape-agnostic: you pass OHLC, a boolean trigger series, and
a function that maps a candidate threshold to a boolean gate. It does the rest.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------------
# ATR (Wilder) -- computed causally, value at bar t uses bars <= t only.
# ----------------------------------------------------------------------------
def wilder_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
    h, l, c = map(lambda x: np.asarray(x, float), (high, low, close))
    prev_c = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))
    atr = np.full(tr.shape, np.nan)
    if tr.size <= period:
        return atr
    atr[period] = tr[1:period + 1].mean()
    alpha = 1.0 / period
    for i in range(period + 1, tr.size):
        atr[i] = (1 - alpha) * atr[i - 1] + alpha * tr[i]
    return atr


# ----------------------------------------------------------------------------
# Barrier-race follow-through for a single trigger bar.
# direction: +1 long, -1 short. Entry at t+1 open.
# Returns: 1 = target hit first (follow-through), 0 = stop hit first (fakeout),
#          np.nan = neither within horizon / insufficient data (excluded).
# ----------------------------------------------------------------------------
def _barrier_outcome(o, h, l, t, direction, atr_t, target_mult, stop_mult, horizon):
    entry_i = t + 1
    if entry_i >= len(o) or not np.isfinite(atr_t) or atr_t <= 0:
        return np.nan
    entry = o[entry_i]
    if direction > 0:
        tgt, stp = entry + target_mult * atr_t, entry - stop_mult * atr_t
    else:
        tgt, stp = entry - target_mult * atr_t, entry + stop_mult * atr_t
    end = min(entry_i + horizon, len(o))
    for i in range(entry_i, end):
        hi, lo = h[i], l[i]
        if direction > 0:
            hit_t, hit_s = hi >= tgt, lo <= stp
        else:
            hit_t, hit_s = lo <= tgt, hi >= stp
        # If both barriers are touched in the same bar we cannot resolve order
        # from daily OHLC -> conservative: count as fakeout (stop-first). This
        # is deliberately pessimistic so the metric never flatters a trigger.
        if hit_t and hit_s:
            return 0
        if hit_t:
            return 1
        if hit_s:
            return 0
    return np.nan  # unresolved within horizon -> excluded, not counted as win


def follow_through_rate(
    ohlc: pd.DataFrame,         # columns: open, high, low, close  (single instrument, time-sorted)
    trigger: np.ndarray,        # boolean, same length; True on bars the trigger fires
    direction: int,
    *,
    target_mult: float = 2.0,
    stop_mult: float = 1.0,
    horizon: int = 10,
    atr_period: int = 14,
) -> tuple[float, int, np.ndarray]:
    """
    Returns (follow_through_rate, n_resolved, per_trigger_outcomes).
    Exit-free: measures whether the move materialised, not what it earned.
    """
    o = ohlc["open"].to_numpy(float)
    h = ohlc["high"].to_numpy(float)
    l = ohlc["low"].to_numpy(float)
    c = ohlc["close"].to_numpy(float)
    atr = wilder_atr(h, l, c, atr_period)

    idx = np.flatnonzero(trigger)
    outcomes = np.full(idx.shape, np.nan)
    for k, t in enumerate(idx):
        outcomes[k] = _barrier_outcome(o, h, l, t, direction, atr[t], target_mult, stop_mult, horizon)
    resolved = outcomes[np.isfinite(outcomes)]
    rate = float(resolved.mean()) if resolved.size else np.nan
    return rate, int(resolved.size), outcomes


# ----------------------------------------------------------------------------
# Threshold sweep with held-out time split + plateau selection.
# ----------------------------------------------------------------------------
@dataclass
class SweepPoint:
    value: float
    train_ft: float
    test_ft: float
    train_n: int
    test_n: int


@dataclass
class SweepResult:
    param_name: str
    base_rate_train: float      # follow-through with NO threshold filter (all triggers)
    base_rate_test: float
    base_n_train: int
    base_n_test: int
    points: list = field(default_factory=list)
    chosen_value: float = float("nan")
    chosen_test_ft: float = float("nan")
    chosen_test_n: int = 0
    plateau: tuple = ()
    is_overfit: bool = False
    note: str = ""


def sweep_threshold(
    ohlc: pd.DataFrame,
    base_trigger: np.ndarray,            # the EVENT, before the parameter gate
    gate_for_value: Callable[[float], np.ndarray],  # value -> boolean gate (same length)
    grid: np.ndarray,
    direction: int,
    train_mask: np.ndarray,              # boolean over bars: in-sample
    test_mask: np.ndarray,               # boolean over bars: out-of-sample (disjoint)
    *,
    param_name: str = "threshold",
    target_mult: float = 2.0,
    stop_mult: float = 1.0,
    horizon: int = 10,
    atr_period: int = 14,
    min_n: int = 30,                     # min resolved trades to trust a grid point
    min_keep_frac: float = 0.05,         # a filter keeping <5% of base triggers is too lossy to trust
    plateau_tol: float = 0.02,           # grid points within this of the train best are "on the plateau"
) -> SweepResult:
    """
    For each grid value v: trigger_v = base_trigger AND gate_for_value(v).
    Measure follow-through on train and on test SEPARATELY. Choose the centre of
    the widest contiguous train-plateau whose test follow-through also clears the
    base rate. Flag overfit if the train-best and test-best diverge.
    """
    def ft(trig, mask):
        t = trig & mask
        return follow_through_rate(ohlc, t, direction,
                                   target_mult=target_mult, stop_mult=stop_mult,
                                   horizon=horizon, atr_period=atr_period)

    base_tr, base_n_tr, _ = ft(base_trigger, train_mask)
    base_te, base_n_te, _ = ft(base_trigger, test_mask)

    pts: list[SweepPoint] = []
    for v in grid:
        trig_v = base_trigger & gate_for_value(v)
        r_tr, n_tr, _ = ft(trig_v, train_mask)
        r_te, n_te, _ = ft(trig_v, test_mask)
        pts.append(SweepPoint(float(v), r_tr, r_te, n_tr, n_te))

    res = SweepResult(
        param_name=param_name,
        base_rate_train=base_tr, base_rate_test=base_te,
        base_n_train=base_n_tr, base_n_test=base_n_te,
        points=pts,
    )

    # candidate points: enough trades, not too lossy, train follow-through beats base
    base_keep = max(1, base_n_tr)
    valid = [p for p in pts
             if p.train_n >= min_n and p.test_n >= min_n
             and p.train_n >= min_keep_frac * base_keep
             and np.isfinite(p.train_ft) and p.train_ft > base_tr]
    if not valid:
        res.note = "no grid point beats base follow-through with adequate sample -> parameter adds no timing edge"
        return res

    train_best = max(valid, key=lambda p: p.train_ft)
    # plateau = contiguous-in-value run around train_best within plateau_tol
    on_plateau = [p for p in valid if (train_best.train_ft - p.train_ft) <= plateau_tol]
    on_plateau.sort(key=lambda p: p.value)
    res.plateau = (on_plateau[0].value, on_plateau[-1].value)
    centre = float(np.median([p.value for p in on_plateau]))
    # snap centre to nearest actually-measured grid point
    chosen = min(valid, key=lambda p: abs(p.value - centre))
    res.chosen_value = chosen.value
    res.chosen_test_ft = chosen.test_ft
    res.chosen_test_n = chosen.test_n

    # overfit check: does the chosen point still beat base OUT of sample?
    test_best = max(valid, key=lambda p: (p.test_ft if np.isfinite(p.test_ft) else -1))
    if not np.isfinite(chosen.test_ft) or chosen.test_ft <= base_te:
        res.is_overfit = True
        res.note = (f"train picks {chosen.value:.3g} (train FT {chosen.train_ft:.3f}) but it does NOT "
                    f"beat base out-of-sample (test FT {chosen.test_ft:.3f} vs base {base_te:.3f}) -> overfit; reject")
    elif abs(test_best.value - chosen.value) > (res.plateau[1] - res.plateau[0] + 1e-9):
        res.note = (f"train optimum {chosen.value:.3g} and test optimum {test_best.value:.3g} disagree beyond the "
                    f"plateau width -> weak/unstable; treat as directional only")
    else:
        lift = chosen.test_ft - base_te
        res.note = (f"chosen {chosen.value:.3g} (plateau {res.plateau[0]:.3g}-{res.plateau[1]:.3g}); "
                    f"out-of-sample follow-through {chosen.test_ft:.3f} vs base {base_te:.3f} (+{lift:.3f}) "
                    f"on n={chosen.test_n}")
    return res


# ----------------------------------------------------------------------------
# Conditional add-test: should a NEW parameter be added GIVEN the existing gates?
# (the gate-redundancy idea, in follow-through units). Compares follow-through of
# {existing gates} vs {existing gates AND new gate}. A new anti-fakeout gate
# earns its place only if it lifts conditional follow-through out-of-sample
# without shrinking the sample below usefulness.
# ----------------------------------------------------------------------------
@dataclass
class AddTestResult:
    new_param: str
    base_ft: float          # existing gates only (test window)
    with_ft: float          # existing AND new gate (test window)
    base_n: int
    with_n: int
    kept_frac: float
    verdict: str
    note: str = ""


def conditional_add_test(
    ohlc: pd.DataFrame,
    existing_trigger: np.ndarray,        # all current gates AND-ed
    new_gate: np.ndarray,                # the candidate anti-fakeout gate
    direction: int,
    test_mask: np.ndarray,
    *,
    new_param: str = "new_gate",
    target_mult: float = 2.0,
    stop_mult: float = 1.0,
    horizon: int = 10,
    atr_period: int = 14,
    min_n: int = 30,
    min_lift: float = 0.03,              # require >=3pp out-of-sample follow-through lift
) -> AddTestResult:
    def ft(trig):
        return follow_through_rate(ohlc, trig & test_mask, direction,
                                   target_mult=target_mult, stop_mult=stop_mult,
                                   horizon=horizon, atr_period=atr_period)
    base_ft, base_n, _ = ft(existing_trigger)
    with_ft, with_n, _ = ft(existing_trigger & new_gate)
    kept = (with_n / base_n) if base_n else 0.0

    if with_n < min_n:
        verdict, note = "DEFER", f"too few surviving trades (n={with_n}) to judge the add"
    elif not np.isfinite(with_ft) or not np.isfinite(base_ft):
        verdict, note = "DEFER", "follow-through unestimable"
    elif (with_ft - base_ft) >= min_lift:
        verdict, note = "ADD", f"lifts follow-through {base_ft:.3f}->{with_ft:.3f} (+{with_ft-base_ft:.3f}) keeping {kept:.0%} of trades"
    elif (with_ft - base_ft) <= -min_lift:
        verdict, note = "REJECT_HARMFUL", f"LOWERS follow-through {base_ft:.3f}->{with_ft:.3f}"
    else:
        verdict, note = "REJECT_REDUNDANT", f"no follow-through lift ({base_ft:.3f}->{with_ft:.3f}) -> just shrinks fires"
    return AddTestResult(new_param, base_ft, with_ft, base_n, with_n, kept, verdict, note)


def format_sweep(res: SweepResult) -> str:
    L = [f"SWEEP {res.param_name}   base follow-through: train {res.base_rate_train:.3f} (n={res.base_n_train}) | test {res.base_rate_test:.3f} (n={res.base_n_test})",
         f"  {'value':>8}{'train_FT':>10}{'test_FT':>9}{'tr_n':>7}{'te_n':>7}"]
    for p in res.points:
        tr = f"{p.train_ft:.3f}" if np.isfinite(p.train_ft) else "  n/a"
        te = f"{p.test_ft:.3f}" if np.isfinite(p.test_ft) else "  n/a"
        mark = "  <-" if p.value == res.chosen_value else ""
        L.append(f"  {p.value:>8.3g}{tr:>10}{te:>9}{p.train_n:>7}{p.test_n:>7}{mark}")
    L.append(f"  => {res.note}")
    if res.is_overfit:
        L.append("  !! OVERFIT FLAG: do not ship this threshold")
    return "\n".join(L)
