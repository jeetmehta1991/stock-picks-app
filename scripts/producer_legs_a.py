"""S6-B3248 / S6-B3304 (B3139q-r162): leg A of spot_check_producer - each
family's producer condition re-derived from RAW BARS with explicit arithmetic
and no import of backtest.signals, so a spot check that agrees has checked
the engine against something other than itself (L582 / L684).

Each function is called (df, i, knobs, leg) - df the cached OHLCV, i the
entry bar's position, knobs the landed arm's {arm key: value} (SPECS
tools.keys), leg 'long' or 'short' - and returns True / False, or None when
the history is too short to decide (counted as SKIPPED, never guessed).

ROUNDING: the producers compare band edges rounded to 4 places (technical.py
compute_bollinger / compute_keltner), so these do too; the moving averages
and deviations are computed by explicit loops, so a last-bit difference from
the pandas kernels can flip only a comparison within 0.00005 of its edge - a
DISAGREE there is a finding about either side (#189)."""
from __future__ import annotations

import math


def _ema(xs: list, span: int) -> list:
    """EMA with adjust=False: e0 = x0, e_t = a x_t + (1 - a) e_{t-1}."""
    a = 2.0 / (span + 1.0)
    out = [float(xs[0])]
    for x in xs[1:]:
        out.append(a * float(x) + (1.0 - a) * out[-1])
    return out


def _atr(h: list, lo: list, c: list, period: int) -> list:
    """Wilder ATR: TR0 = h0 - l0, TR_t = max(h - l, |h - c_{t-1}|, |l - c_{t-1}|),
    smoothed with alpha 1 / period and adjust=False."""
    tr = [float(h[0]) - float(lo[0])]
    for t in range(1, len(h)):
        tr.append(max(h[t] - lo[t], abs(h[t] - c[t - 1]), abs(lo[t] - c[t - 1])))
    a = 1.0 / period
    out = [tr[0]]
    for x in tr[1:]:
        out.append(a * x + (1.0 - a) * out[-1])
    return out


def _in_squeeze(c: list, h: list, lo: list, j: int, bb_k: float, kc_p: int,
                kc_m: float) -> bool | None:
    """The squeeze state at bar j: Bollinger (20, bb_k) inside Keltner
    (kc_p, kc_m x ATR kc_p), edges rounded to 4 places. None below the
    producer's history floors (22 bars for the Bollinger edges, kc_p + 2 for
    the channel)."""
    n = j + 1
    if n < max(22, kc_p + 2):
        return None
    w = [float(x) for x in c[j - 19:j + 1]]
    mid = sum(w) / 20.0
    sd = math.sqrt(sum((x - mid) ** 2 for x in w) / 19.0)
    ema = _ema(c[:n], kc_p)[-1]
    atr = _atr(h[:n], lo[:n], c[:n], kc_p)[-1]
    bl, bu = round(mid - bb_k * sd, 4), round(mid + bb_k * sd, 4)
    kl, ku = round(ema - kc_m * atr, 4), round(ema + kc_m * atr, 4)
    return bl > kl and bu < ku


def _momentum(c: list, h: list, lo: list, j: int, w: int) -> float:
    """The close minus the w-bar high / low midpoint at bar j (the producer's
    squeeze_momentum before its rounding)."""
    hh = max(h[j - w + 1:j + 1])
    ll = min(lo[j - w + 1:j + 1])
    return c[j] - (hh + ll) / 2.0


def squeeze_fire(df, i: int, knobs: dict, leg: str):
    """squeeze_fire_up (long) / squeeze_fire_dn (short) at bar i: NOT in a
    squeeze on bar i, the close-minus-midpoint momentum crossing zero in the
    leg's direction, and - when prior_n > 0 - a squeeze on at least one of the
    prior_n bars before i."""
    kc_m, bb_k = float(knobs["kc_mult"]), float(knobs["bb_std"])
    w, kc_p, n = int(knobs["mom_window"]), int(knobs["kc_period"]), int(knobs["prior_n"])
    c = [float(x) for x in df["close"].values[:i + 1]]
    h = [float(x) for x in df["high"].values[:i + 1]]
    lo = [float(x) for x in df["low"].values[:i + 1]]
    if i + 1 < max(22, kc_p + 2, w + 1):
        return None
    now = _in_squeeze(c, h, lo, i, bb_k, kc_p, kc_m)
    if now is None:
        return None

    m, pm = _momentum(c, h, lo, i, w), _momentum(c, h, lo, i - 1, w)
    cross = (m > 0 and pm <= 0) if leg == "long" else (m < 0 and pm >= 0)
    released = n <= 0 or any(_in_squeeze(c, h, lo, i - k, bb_k, kc_p, kc_m)
                             for k in range(1, n + 1) if i - k >= 0)
    return (not now) and cross and bool(released)


def camarilla_break(df, i: int, knobs: dict, leg: str):
    """above_cam_r4 (long) / below_cam_s4 (short) at bar i: the close beyond
    the prior close +/- dist x the prior bar's range (dist 0.55 = 1.1 / 2,
    evaluated as the producer's own expression)."""
    if i < 1:
        return None
    d = float(knobs["dist"])
    C = float(df["close"].values[i - 1])
    rng = float(df["high"].values[i - 1]) - float(df["low"].values[i - 1])
    today = float(df["close"].values[i])
    if leg == "long":
        r4 = C + rng * 1.1 / 2 if d == 0.55 else C + rng * d
        return today > r4
    s4 = C - rng * 1.1 / 2 if d == 0.55 else C - rng * d
    return today < s4
