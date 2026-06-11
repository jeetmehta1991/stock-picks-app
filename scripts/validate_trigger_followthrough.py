"""
validate_trigger_followthrough.py

Ground-truth synthetic market. We CONTROL which breakouts follow through and
which are fakeouts, and we control the parameter that separates them. Then we
check the tool recovers it honestly.

Construction:
  - Random-walk-ish price with occasional "breakout" bars (the EVENT).
  - Each breakout has a hidden quality q ~ U(0,1).
  - The breakout's CLEARANCE above the level is correlated with q (real breaks
    clear by more). So clearance is a TRUE separating parameter.
  - Follow-through is generated from q: high-q breaks drift up (target-first),
    low-q breaks reverse (stop-first).
  - We ALSO add a decoy parameter that is pure noise (uncorrelated with q) to
    confirm the tool REJECTS it.

Checks:
  (1) sweep_threshold on clearance recovers a threshold that lifts out-of-sample
      follow-through above base, on a plateau, not overfit.
  (2) sweep_threshold on the NOISE decoy returns "no edge" / overfit-rejected.
  (3) conditional_add_test ADDs the real clearance gate and REJECTs the decoy.
"""

import numpy as np
import pandas as pd

from trigger_followthrough import (
    sweep_threshold, conditional_add_test, follow_through_rate, format_sweep,
)

rng = np.random.default_rng(7)
N = 12_000

# ---- build a price path with embedded breakouts of known quality ----
open_ = np.zeros(N); high = np.zeros(N); low = np.zeros(N); close = np.zeros(N)
trigger = np.zeros(N, bool)
clearance_atr = np.zeros(N)     # observable param: how far the break cleared, in ATR
decoy = np.zeros(N)             # observable param: pure noise
quality = np.full(N, np.nan)    # hidden ground truth

price = 100.0
vol = 1.0
pending_drift = np.zeros(N)   # quality-driven drift scheduled into future bars
DRIFT_BARS = 12

for i in range(N):
    is_break = (i > 60) and (rng.random() < 0.04)
    o = price
    if is_break:
        q = rng.random()
        quality[i] = q
        clr = np.clip(0.15 + 0.9 * q + rng.normal(0, 0.25), 0.0, 3.0)
        clearance_atr[i] = clr
        decoy[i] = rng.random()
        trigger[i] = True
        c = o + clr * vol
        h = c + 0.2 * vol
        l = o - 0.1 * vol
        # schedule a PERSISTENT directional drift over the next DRIFT_BARS bars,
        # sign & size set by quality. high q -> sustained up (target-first),
        # low q -> sustained down (stop-first). magnitude per bar tuned so the
        # 2*ATR target / 1*ATR stop race is genuinely decided by q.
        per_bar = (q - 0.5) * 0.55 * vol
        j0 = i + 1
        for j in range(j0, min(j0 + DRIFT_BARS, N)):
            pending_drift[j] += per_bar
    else:
        c = o + rng.normal(0, 0.5) * vol
        h = max(o, c) + abs(rng.normal(0, 0.3)) * vol
        l = min(o, c) - abs(rng.normal(0, 0.3)) * vol
    open_[i], high[i], low[i], close[i] = o, h, l, c
    price = c + pending_drift[i] + rng.normal(0, 0.35) * vol

ohlc = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close})

# train / test split in time (disjoint)
train_mask = np.zeros(N, bool); train_mask[:N // 2] = True
test_mask = np.zeros(N, bool);  test_mask[N // 2:] = True

print("=" * 78)
base_rate, base_n, _ = follow_through_rate(ohlc, trigger, direction=+1,
                                           target_mult=2.0, stop_mult=1.0, horizon=12)
print(f"Unfiltered breakout follow-through (all triggers): {base_rate:.3f} on n={base_n}")
print("  (this is the base rate a good clearance filter should beat)\n")

# ---- (1) sweep the REAL separating parameter: clearance ----
grid = np.round(np.arange(0.2, 1.6, 0.1), 2)
def clearance_gate(v):
    return clearance_atr >= v
res = sweep_threshold(ohlc, trigger, clearance_gate, grid, direction=+1,
                      train_mask=train_mask, test_mask=test_mask,
                      param_name="break_clearance_atr",
                      target_mult=2.0, stop_mult=1.0, horizon=12)
print(format_sweep(res))
real_ok = (not res.is_overfit) and np.isfinite(res.chosen_value) and res.chosen_test_ft > res.base_rate_test
print(f"  CHECK real-parameter recovered + OOS-valid: {'PASS' if real_ok else 'FAIL'}")
print("-" * 78)

# ---- (2) sweep the NOISE decoy: tool must NOT find a shippable threshold ----
def decoy_gate(v):
    return decoy >= v
res_decoy = sweep_threshold(ohlc, trigger, decoy_gate, np.round(np.arange(0.1, 0.9, 0.1), 2),
                            direction=+1, train_mask=train_mask, test_mask=test_mask,
                            param_name="decoy_noise",
                            target_mult=2.0, stop_mult=1.0, horizon=12)
print(format_sweep(res_decoy))
decoy_ok = res_decoy.is_overfit or not np.isfinite(res_decoy.chosen_value) or res_decoy.chosen_test_ft <= res_decoy.base_rate_test + 1e-9
print(f"  CHECK noise decoy rejected/over-fit-flagged: {'PASS' if decoy_ok else 'FAIL'}")
print("-" * 78)

# ---- (3) conditional add-test: add real clearance gate vs add decoy ----
# existing trigger = raw breakout; candidate gates as boolean
add_real = conditional_add_test(ohlc, trigger, clearance_atr >= 0.6, direction=+1,
                                test_mask=test_mask, new_param="clearance>=0.6",
                                target_mult=2.0, stop_mult=1.0, horizon=12)
add_decoy = conditional_add_test(ohlc, trigger, decoy >= 0.5, direction=+1,
                                 test_mask=test_mask, new_param="decoy>=0.5",
                                 target_mult=2.0, stop_mult=1.0, horizon=12)
print(f"ADD real clearance gate -> {add_real.verdict}: {add_real.note}")
print(f"ADD decoy noise gate    -> {add_decoy.verdict}: {add_decoy.note}")
add_ok = add_real.verdict == "ADD" and add_decoy.verdict in ("REJECT_REDUNDANT", "REJECT_HARMFUL", "DEFER")
print(f"  CHECK add-test accepts real / rejects decoy: {'PASS' if add_ok else 'FAIL'}")
print("=" * 78)

print(f"\nALL CHECKS: {'PASS' if (real_ok and decoy_ok and add_ok) else 'FAIL'}")
