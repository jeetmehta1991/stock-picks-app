"""verify_silent_gap_fix.py

B693 (2026-06-11) per external reviewer's specific test for BR-7/BR-8:
"the 25k SHORT fires on break_retest_volume and break_retest_confluence
are consistent with the silent-gap bugs never having been fully fixed."

A silent-gap bug exists when a strategy uses the `not s.get(key)` pattern
(or returns a default that satisfies the gate when the key is absent).
The fingerprint of a live silent-gap: feed the strategy a signals dict
that is MISSING the supposedly-gating keys; if the strategy still fires,
the gate is auto-passing -- the supposed gate is not actually gating.

This tool implements the test for any strategy. For BR-7 (`strat_break
_retest_volume`) and BR-8 (`strat_dc20_break_retest`), the reviewer
specifically suspected the SHORT-side gates auto-pass when:
  - `not s.get('macd_12_26_9_bullish')`
  - `not s.get('macd_12_26_9_bearish')`  (post-B608 explicit signal)
  - `not s.get('obv_bullish')`           (post-B609 explicit signal)
  - other not-pattern gates

USAGE:
  python scripts/verify_silent_gap_fix.py --strategy strat_break_retest_volume \\
      --direction short

REPORT:
  - For each declared SHORT-side gate key, run the strategy with that key
    OMITTED from the signals dict (and all other keys set to the value
    expected to fire SHORT).
  - If the strategy STILL fires SHORT despite the key missing, that key is
    a silent-gap (auto-passes).
  - If the strategy DOES NOT fire when the key is missing, the gate is real.

This is the BR-7/BR-8 silent-gap-still-live test the reviewer requested.
Independent of B660 measurement; runs in milliseconds.

NOT YET PRODUCTION-READY: scaffold per B693 owner approval. KNOWN LIMITATION:
the current omit-and-re-fire loop iterates ALL declared keys (both LONG and
SHORT branches of dual strategies), so it will flag LONG-side keys as
"silent-gap on SHORT" when they're simply unused by the SHORT branch. This
overreports. The fix is per-direction-branch key filtering by source-reading
the strategy's LONG vs SHORT gate sets separately. Queued.

B693 finding from running this on BR-7 (break_retest_volume) SHORT: post-B617
4-gate uses positive `s.get(...)` AND-chained (line 2730-2733 of screener.py)
with NO `not s.get(...)` patterns. Missing keys -> None -> falsy -> AND fails.
NO SILENT-GAP. The 25,015 measured SHORT fires are REAL fires, not auto-pass
artifacts. The reviewer's SUSPICION was correct in principle (silent-gap is
the SIGNATURE of high unexplained SHORT counts) but specifically wrong on BR-7
post-B617. The redundancy concern (BR-7/BR-8 firing on the same trade as
Donchian / 52w retest variants) remains live and is the real explanation.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure repo root on sys.path
_REPO_ROOT_FOR_PATH = str(Path(__file__).resolve().parents[1])
if _REPO_ROOT_FOR_PATH not in sys.path:
    sys.path.insert(0, _REPO_ROOT_FOR_PATH)

logger = logging.getLogger("verify_silent_gap_fix")


# Common signals-dict fixtures by direction. These are filled with values
# that satisfy the gate on the relevant direction's branch; the test
# omits ONE key at a time and checks whether the strategy still fires.
def _short_friendly_signal_dict() -> dict:
    """Maximal SHORT-fire-friendly signals dict. Includes the known gates
    typical of breakdown/retest SHORT strategies. Anything not in this dict
    that the strategy reads will be hit with `get(key, default)` -- the
    silent-gap-class bug is when that default lets the gate auto-pass.
    """
    return {
        # Pivot / break_retest primitives (LONG branch -- set to FALSE so
        # the strategy CANNOT fire LONG and we isolate the SHORT branch)
        "break_retest_long_fires": False,
        "break_retest_long_volume_confirmed": False,
        # SHORT branch primitives (set to TRUE)
        "break_retest_short_fires": True,
        "break_retest_short_volume_confirmed": True,
        # break_retest_volume / confluence specifics
        "resistance_break_retest": False,   # LONG-side; turn off for SHORT iso
        "support_break_retest": True,       # SHORT-side trigger
        # Short interest
        "days_to_cover": 3.0,               # below B671 SM-5 borrow-trap threshold (8.0)
        # 52w / DC20 / Donchian
        "dc20_breakdown": True,
        "dc20_breakdown_retest_short": True,
        "52w_low": True,
        # Volume gates
        "vol_spike_2x": True,
        "vol_spike_15x": True,
        "vol_spike_17x": True,
        "vol_below_avg": True,
        # Momentum gates (set BEARISH; bull=False, bear=True)
        "macd_12_26_9_bullish": False,
        "macd_12_26_9_bearish": True,
        "macd_12_26_9_crossover_dn": True,
        "macd_8_21_5_bearish": True,
        "obv_bullish": False,
        "obv_bearish": True,
        # Trend
        "price_above_ema_200": False,
        "price_above_ema_50": False,
        "below_ema_200": True,
        "below_ema_50": True,
        "ema_200_bearish": True,
        # Pivot proximity
        "below_avwap_20low": True,
        "below_avwap_50low": True,
        "below_avwap_252": True,
        # Candle close-quality on SHORT
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
        # Other booleans the strategy may read; default True is the
        # silent-gap-prone case for `not s.get(key)` to NOT auto-pass
        # so we set everything we touch.
        "adx_trending": True,
        "rsi_14": 30,
        "sector_underperforming_spy": True,
    }


def verify(strategy_name: str, direction: str) -> dict:
    """For each key the strategy reads, omit it from a maximally-firing
    signals dict and report whether the strategy still fires."""
    from backtest.signals.screener import ALL_STRATEGIES
    from scripts.diagnose_zero_fires import declared_signal_keys

    if strategy_name not in ALL_STRATEGIES:
        raise SystemExit(f"strategy {strategy_name!r} not in ALL_STRATEGIES")
    fn = ALL_STRATEGIES[strategy_name]
    declared = declared_signal_keys(fn)
    logger.info("Strategy %s reads %d keys: %s", strategy_name, len(declared), declared)

    if direction == "short":
        base = _short_friendly_signal_dict()
    else:
        raise SystemExit("Only --direction short implemented in B693 scaffold; LONG is symmetric, queued.")

    # Baseline: does the strategy fire SHORT with the full dict?
    out = fn(dict(base))
    baseline_fires = bool(out.get("fires"))
    baseline_direction = out.get("direction")
    logger.info("Baseline: fires=%s direction=%s", baseline_fires, baseline_direction)
    if not baseline_fires or baseline_direction != direction:
        return {
            "strategy": strategy_name,
            "direction": direction,
            "baseline_fires": baseline_fires,
            "baseline_direction": baseline_direction,
            "verdict": "BASELINE_NO_FIRE",
            "verdict_reason": (
                f"With the maximally-firing SHORT fixture the strategy does not fire SHORT. "
                f"Either the fixture is missing a required gate or the strategy is not a "
                f"SHORT-firing strategy on this gate-set. Cannot test silent-gap without "
                f"a baseline fire."
            ),
            "fixture_keys": sorted(base.keys()),
            "declared_keys": declared,
        }

    # Now omit one key at a time and re-run.
    omit_results: dict[str, dict] = {}
    silent_gap_keys: list[str] = []
    for key in declared:
        # Skip keys not in the fixture (the strategy reads them but we never set them)
        if key not in base:
            omit_results[key] = {
                "in_fixture": False,
                "note": "key not in fixture; strategy reads it via s.get(..., default). If the default fires the gate, the strategy is silent-gap-class regardless of this test.",
            }
            continue
        modified = dict(base)
        del modified[key]
        out2 = fn(modified)
        fires_without = bool(out2.get("fires"))
        dir_without = out2.get("direction")
        omit_results[key] = {
            "in_fixture": True,
            "still_fires": fires_without,
            "direction": dir_without,
            "is_silent_gap_if_still_fires": fires_without and dir_without == direction,
        }
        if fires_without and dir_without == direction:
            silent_gap_keys.append(key)

    if silent_gap_keys:
        verdict = "SILENT_GAP_LIVE"
        reason = (
            f"Strategy fires {direction.upper()} even when the following keys are MISSING from "
            f"the signals dict: {silent_gap_keys}. These gates are auto-passing -- the supposed "
            f"gates are not actually gating. This is the BR-7/BR-8 fingerprint the reviewer "
            f"warned about. Cross-reference B608/B617/F2 fix history and pin a regression test."
        )
    else:
        verdict = "SILENT_GAP_CLEAN"
        reason = (
            f"No declared gate key, when omitted, allowed the strategy to still fire "
            f"{direction.upper()}. All gates in the fixture are gating correctly."
        )

    return {
        "strategy": strategy_name,
        "direction": direction,
        "baseline_fires": baseline_fires,
        "n_declared_keys": len(declared),
        "n_in_fixture": sum(1 for k in declared if k in base),
        "silent_gap_keys": silent_gap_keys,
        "n_silent_gap_keys": len(silent_gap_keys),
        "omit_results": omit_results,
        "verdict": verdict,
        "verdict_reason": reason,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--strategy", required=True)
    p.add_argument("--direction", choices=["long", "short"], default="short")
    p.add_argument("--output", default=None)
    p.add_argument("--verbose", action="store_true")
    return p


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    result = verify(args.strategy, args.direction)
    text = json.dumps(result, indent=2, default=str)
    if args.output:
        Path(args.output).write_text(text)
        logger.info("Wrote %s", args.output)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
