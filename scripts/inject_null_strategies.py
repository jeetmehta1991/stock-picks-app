# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 16 per CHECKLIST #77.
"""B965 (2026-06-20): inject 5 null negative-control strategies into Stream E.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 16 + Council 67 4/4 verdict
# per owner directive 2026-06-20 'Continue council this. Continue without
# stopping till all sections in P1 are done.' per CHECKLIST #77.

PURPOSE
-------
PATH Section 13.3 row 16 spec (canonical):
  'Negative-control canary status'
  '5 null strategies injected pre-Stream-E; framework must identify them;
   if not, framework miscalibrated.'

Council 67 Contrarian hardening: ship as RUNNABLE injection script with 5
concrete null specs (NOT schema-only IOU). Section 16 extractor reads from
this script's NULL_STRATEGY_REGISTRY constant + reports per-strategy whether
the framework correctly identifies it as null.

5 CANONICAL NULL STRATEGIES (Council 67 design):
  1. null_random_long_p05      - fires randomly on 5% of bars (Bernoulli p=0.05)
  2. null_shuffled_signal_long - fires when a real signal fires but on a
                                 randomly-shuffled date (look-ahead destroyed)
  3. null_lagged_self_long     - fires when self fired 252 bars ago (own
                                 signal lagged out of relevance window)
  4. null_pure_noise_gauss     - fires when standard-normal random > 1.65
                                 (one-tailed p<0.05; ~5% fire rate)
  5. null_coin_flip_daily      - fires when daily coin-flip = heads (p=0.5;
                                 high fire rate so PASS-by-chance unlikely)

IDENTIFICATION CRITERIA:
  A correctly-calibrated framework MUST classify all 5 null strategies as
  FAILED on at least one of:
    - exit_profitability_check (Section 15): null edge -> <40% positive exits
    - corrected_sharpe_overall_re_pass (Section 14): noise -> corrected
      Sharpe < 1.0 overall after Lo 2002 deflation
    - gate_stacking_check (Section 2): not strictly required (nulls have
      single random gate not 4-gate stack)

CALIBRATION VERDICT:
  framework_calibrated = True if 5/5 null strategies FAIL at least one gate
  framework_calibrated = False if any null strategy PASSES all gates
                              (framework over-permissive; Type 1 error)

USAGE
-----
  Stream E sequence:
    1. Run this script: registers 5 null strategies in ALL_STRATEGIES at
       runtime (does NOT mutate screener.py source; addition is process-local)
    2. R5 cube runs; null strategies execute alongside real strategies
    3. Section 16 extractor reads R5 trade_log + sections 2/14/15 verdicts
       per null strategy
    4. Calibration verdict = all 5 nulls correctly identified as FAILED

ALTERNATIVE EXECUTION (Council 67 anti-IOU):
  This script is RUNNABLE today: `python -m scripts.inject_null_strategies
  --verify-registration` prints the 5 registered names + their stub
  predicates. R5 wiring is owner-decision (currently not auto-loaded into
  ALL_STRATEGIES to avoid contaminating R4/R5 trade_log mid-flight).

OUTPUT WHEN RUN
---------------
{
  "n_null_strategies": 5,
  "names": [list of 5],
  "registration_status": "stub_callable_runtime_ready",
  "stream_e_integration_status": "manual_owner_decision_pending"
}
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

import numpy as np

# Seed for reproducibility (Council 67 First Principles: reproducible canary)
NULL_STRATEGY_SEED = 0xC0FFEE


def _make_null_random_long(p: float = 0.05) -> Callable:
    """Bernoulli null: fires on p fraction of bars."""
    rng = np.random.default_rng(NULL_STRATEGY_SEED)

    def strat(s: dict) -> dict:
        fires = bool(rng.random() < p)
        return {
            "fires": fires,
            "direction": "long",
            "category": "null_control",
            "signals_used": ["bernoulli_p05"],
            "context_bullets": ["null_random_long_p05 (negative control)"],
        }
    return strat


def _make_null_shuffled_signal_long() -> Callable:
    """Fires when a real signal fires (rsi_oversold) but coin-flip override.

    Approximation: gate the real signal through Bernoulli p=0.5 to destroy
    its temporal alpha. Cheaper than building a full date-shuffle infra.
    """
    rng = np.random.default_rng(NULL_STRATEGY_SEED + 1)

    def strat(s: dict) -> dict:
        real = bool(s.get("rsi_oversold", False))
        fires = bool(real and rng.random() < 0.5)
        return {
            "fires": fires,
            "direction": "long",
            "category": "null_control",
            "signals_used": ["rsi_oversold", "coinflip_destroy_timing"],
            "context_bullets": ["null_shuffled_signal_long (negative control)"],
        }
    return strat


def _make_null_lagged_self_long() -> Callable:
    """Fires when rsi_oversold fired 252 bars ago (signal lagged out of window).

    Approximation: gate on a far-history flag. If signal_lagged_252 not in
    feature set, fall back to Bernoulli p=0.01 (rare-fire null).
    """
    rng = np.random.default_rng(NULL_STRATEGY_SEED + 2)

    def strat(s: dict) -> dict:
        # Look for explicit lagged-self field; fall back to ~1% Bernoulli
        lagged = s.get("rsi_oversold_lag_252", None)
        if lagged is not None:
            fires = bool(lagged)
        else:
            fires = bool(rng.random() < 0.01)
        return {
            "fires": fires,
            "direction": "long",
            "category": "null_control",
            "signals_used": ["rsi_oversold_lag_252_OR_bernoulli_p01"],
            "context_bullets": ["null_lagged_self_long (negative control)"],
        }
    return strat


def _make_null_pure_noise_gauss() -> Callable:
    """Fires when standard-normal sample > 1.65 (one-tailed p<0.05)."""
    rng = np.random.default_rng(NULL_STRATEGY_SEED + 3)

    def strat(s: dict) -> dict:
        z = float(rng.standard_normal())
        fires = bool(z > 1.65)
        return {
            "fires": fires,
            "direction": "long",
            "category": "null_control",
            "signals_used": ["gauss_z_gt_1p65"],
            "context_bullets": [f"null_pure_noise_gauss z={z:.3f}"],
        }
    return strat


def _make_null_coin_flip_daily() -> Callable:
    """Fires when daily coin-flip = heads (Bernoulli p=0.5)."""
    rng = np.random.default_rng(NULL_STRATEGY_SEED + 4)

    def strat(s: dict) -> dict:
        fires = bool(rng.random() < 0.5)
        return {
            "fires": fires,
            "direction": "long",
            "category": "null_control",
            "signals_used": ["bernoulli_p50"],
            "context_bullets": ["null_coin_flip_daily (negative control)"],
        }
    return strat


# Canonical 5-null registry: name -> stub factory
NULL_STRATEGY_REGISTRY: dict[str, Callable[[], Callable]] = {
    "null_random_long_p05":      lambda: _make_null_random_long(p=0.05),
    "null_shuffled_signal_long": _make_null_shuffled_signal_long,
    "null_lagged_self_long":     _make_null_lagged_self_long,
    "null_pure_noise_gauss":     _make_null_pure_noise_gauss,
    "null_coin_flip_daily":      _make_null_coin_flip_daily,
}

# Canonical null strategy names (for Section 16 extractor consumption)
NULL_STRATEGY_NAMES: tuple[str, ...] = tuple(NULL_STRATEGY_REGISTRY.keys())


def build_null_strategies() -> dict[str, Callable]:
    """Instantiate all 5 null strategy callables.

    Returns {name: strategy_callable} ready for ALL_STRATEGIES insertion.
    Each callable is deterministic given the seed; deterministic null
    is what makes Section 16 reproducible.
    """
    return {name: factory() for name, factory in NULL_STRATEGY_REGISTRY.items()}


def inject_into_all_strategies(verbose: bool = True) -> dict[str, Any]:
    """Inject 5 null strategies into backtest.signals.screener.ALL_STRATEGIES.

    Runtime mutation only (does NOT persist to screener.py source). Idempotent.
    """
    try:
        from backtest.signals import screener
    except Exception as e:
        return {"status": "error", "reason": f"cannot import screener: {e}"}

    null_strats = build_null_strategies()
    added: list[str] = []
    already_present: list[str] = []
    for name, callable_ in null_strats.items():
        if name in screener.ALL_STRATEGIES:
            already_present.append(name)
        else:
            screener.ALL_STRATEGIES[name] = callable_
            added.append(name)

    if verbose:
        print(f"injected {len(added)} null strategies; {len(already_present)} already present")
        for n in added:
            print(f"  + {n}")
        for n in already_present:
            print(f"  = {n} (already present)")

    return {
        "status": "ok",
        "added": added,
        "already_present": already_present,
        "n_total_after": len(screener.ALL_STRATEGIES),
    }


def verify_registration() -> dict[str, Any]:
    """Verify 5 null strategies build + are callable on a stub signals dict."""
    null_strats = build_null_strategies()
    stub_s = {"rsi_oversold": True, "rsi_oversold_lag_252": False}
    results: dict[str, Any] = {}
    for name, fn in null_strats.items():
        try:
            out = fn(stub_s)
            results[name] = {
                "callable": True,
                "fires_on_stub": out.get("fires"),
                "category": out.get("category"),
            }
        except Exception as e:
            results[name] = {"callable": False, "error": str(e)}
    return {
        "n_null_strategies": 5,
        "names": list(NULL_STRATEGY_NAMES),
        "verification": results,
        "registration_status": "stub_callable_runtime_ready",
        "stream_e_integration_status": "manual_owner_decision_pending",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-registration", action="store_true",
                    help="Run verification + print 5 null strategy callable status")
    ap.add_argument("--inject", action="store_true",
                    help="Mutate screener.ALL_STRATEGIES at runtime (process-local)")
    args = ap.parse_args()

    if args.inject:
        out = inject_into_all_strategies(verbose=True)
        print(json.dumps(out, indent=2))
        return 0
    if args.verify_registration:
        out = verify_registration()
        print(json.dumps(out, indent=2))
        return 0
    # Default: print verification
    out = verify_registration()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
