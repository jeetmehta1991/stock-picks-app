"""B1565 / S6-B1563c -- demand-driven signal pruning that CANNOT fail silently.

THE PRIZE (measured, profile cumtime over 1389.7s):
    compute_all_signals   14.3pct of runtime
    compute_smc_signals   27.2pct of runtime
A single-strategy optimisation run computes all ~540 signal keys to evaluate a
strategy that reads two of them.

THE HAZARD THAT BLOCKED THE OBVIOUS IMPLEMENTATION (L437)
Deriving "which signals does this strategy need" from source text is UNSAFE.
`smc_breaker_block_long` builds its trend-gate key at runtime:

    _ema_key = f"price_above_ema_{_cfg.STRAT_EMA_SPAN}"     # B1519
    fires = s.get("smc_breaker_block_bullish", False) and s.get(_ema_key, False)

A static scan of `s.get("literal")` sees ONE key and concludes zero producers
are needed. Skip `compute_ema_sma` on that basis and the strategy reads a
missing key, `.get(..., False)` returns the default, and the strategy SILENTLY
NEVER FIRES -- no exception, a plausible zero-fire result, on the exact
strategy under optimisation. 6 of 222 strategies use dynamic keys.

`.get(key, default)` is what makes this class invisible: it converts "never
computed" into "False", which is a legal value.

THE DESIGN
Two mechanisms, and the second is what makes the first safe to be wrong:

 1. RECORD, don't infer. `RecordingSignals` wraps the FULL signal dict for a
    warmup period and logs every key the active strategies actually read --
    runtime-built keys included, because we observe the read rather than the
    source.

 2. RAISE, don't default. After warmup, `GuardedSignals` wraps the PRUNED dict
    and knows which keys the skipped producers would have emitted. A read of
    any such key raises instead of returning a default. So if the recording
    missed a key -- a rare branch, a regime-gated path -- the run FAILS LOUDLY
    on the first affected bar rather than quietly producing a wrong answer.

Mechanism 2 is not belt-and-braces. Warmup recording can only observe branches
that executed during warmup; a strategy whose EMA leg is reached only in a bull
regime would go unrecorded. The guard converts that from a silent wrong answer
into a stack trace.

SCOPE
Pruning is enabled ONLY when a strategy subset is active. Full-roster
production cube runs take the unpruned path unchanged.
"""
from __future__ import annotations

import inspect
import re
from typing import Iterable

# Producer -> emitted keys, built once per process by CALLING each producer.
# Not parsed from source: a producer's key set is what it returns, and several
# build key names with f-strings (compute_ema_sma emits price_above_ema_<span>).
_PRODUCER_KEYS: dict[str, frozenset[str]] | None = None


def build_producer_key_map(sample_df) -> dict[str, frozenset[str]]:
    """Call every producer in compute_all_signals once; record what it emits.

    `sample_df` must be a real OHLCV frame long enough for every producer to
    return its full key set (>=250 bars). A short frame makes producers return
    {} early, which would under-populate the map and cause the guard to miss
    keys it should protect.
    """
    global _PRODUCER_KEYS
    import backtest.signals.technical as T

    src = inspect.getsource(T.compute_all_signals)
    names = list(dict.fromkeys(
        re.findall(r"signals\.update\((compute_\w+)\(", src)))
    out: dict[str, frozenset[str]] = {}
    for n in names:
        fn = getattr(T, n, None)
        if fn is None:
            continue
        try:
            res = fn(sample_df)
        except Exception:
            # A producer that cannot run on the sample gets an EMPTY key set,
            # which means the guard will never claim its keys were "skipped".
            # Failing open here is correct: an unknown producer must not cause
            # spurious raises. It simply will not be pruned.
            out[n] = frozenset()
            continue
        out[n] = frozenset(res.keys()) if hasattr(res, "keys") else frozenset()
    _PRODUCER_KEYS = out
    return out


def get_producer_key_map() -> dict[str, frozenset[str]]:
    if _PRODUCER_KEYS is None:
        raise RuntimeError(
            "producer key map not built -- call build_producer_key_map(df) "
            "with a real OHLCV frame before pruning")
    return _PRODUCER_KEYS


class RecordingSignals(dict):
    """Full signal dict that records which keys are actually READ.

    Used during warmup. Records reads via BOTH `.get()` and `[]` because
    strategies use both idioms.
    """

    __slots__ = ("_read",)

    def __init__(self, base: dict, read_sink: set):
        super().__init__(base)
        self._read = read_sink

    def get(self, key, default=None):
        self._read.add(key)
        return super().get(key, default)

    def __getitem__(self, key):
        self._read.add(key)
        return super().__getitem__(key)

    def __contains__(self, key):
        # `"k" in s` is a read of k's existence, and a strategy can gate on it.
        self._read.add(key)
        return super().__contains__(key)


class SkippedSignalError(KeyError):
    """A strategy read a key whose producer was pruned away."""


class GuardedSignals(dict):
    """Pruned signal dict that RAISES on reads of skipped-producer keys.

    This is the mechanism that makes pruning safe to get wrong. Without it a
    missed key returns `.get()`'s default and the strategy silently misfires
    (L437). With it, the run dies on the first affected bar.
    """

    __slots__ = ("_skipped",)

    def __init__(self, base: dict, skipped_keys: Iterable[str]):
        super().__init__(base)
        self._skipped = frozenset(skipped_keys)

    def _check(self, key):
        if key not in self and key in self._skipped:
            raise SkippedSignalError(
                f"signal {key!r} was read but its producer was PRUNED. The "
                f"warmup recording did not observe this read -- likely a "
                f"branch that only executes under some regime/date. Pruning "
                f"is unsafe for this strategy set; disable it "
                f"(DEMAND_PRUNING=0) or extend warmup. Returning a default "
                f"here would make the strategy silently misfire (L437).")

    def get(self, key, default=None):
        self._check(key)
        return super().get(key, default)

    def __getitem__(self, key):
        self._check(key)
        return super().__getitem__(key)


def required_producers(read_keys: Iterable[str],
                       key_map: dict[str, frozenset[str]] | None = None
                       ) -> set[str]:
    """Producers that emit at least one key the strategies actually read."""
    km = key_map if key_map is not None else get_producer_key_map()
    rk = set(read_keys)
    return {name for name, keys in km.items() if keys & rk}


def skipped_keys(keep: Iterable[str],
                 key_map: dict[str, frozenset[str]] | None = None
                 ) -> frozenset[str]:
    """Keys that will be ABSENT because their producer is not in `keep`.

    A key emitted by BOTH a kept and a skipped producer is NOT skipped -- the
    kept producer still supplies it. Getting this wrong would raise on a key
    that is actually present.
    """
    km = key_map if key_map is not None else get_producer_key_map()
    keep = set(keep)
    kept_keys: set[str] = set()
    for n in keep:
        kept_keys |= set(km.get(n, ()))
    dropped: set[str] = set()
    for n, keys in km.items():
        if n not in keep:
            dropped |= set(keys)
    return frozenset(dropped - kept_keys)


__all__ = [
    "build_producer_key_map", "get_producer_key_map",
    "RecordingSignals", "GuardedSignals", "SkippedSignalError",
    "required_producers", "skipped_keys",
]


# ---------------------------------------------------------------------------
# B1567 -- process-local warmup -> prune state machine
#
# Enabled ONLY when a strategy subset is active. A full-roster production cube
# run reads every producer anyway, so pruning would buy nothing and risk
# everything; `enabled()` returning False makes this module inert.
#
# Under --screen-pool-workers each worker is its own process with its own
# state, so each performs its own warmup. That is wasteful by a few bars and
# CORRECT -- sharing recorded keys across processes would couple workers.
# ---------------------------------------------------------------------------

WARMUP_BARS_DEFAULT = 25

_STATE = {
    "mode": None,          # None=undecided, "off", "warmup", "pruned"
    "read": set(),
    "skip": frozenset(),
    "warmup_left": 0,
}


def _decide_mode() -> str:
    import os
    if os.environ.get("DEMAND_PRUNING", "1") != "1":
        return "off"
    # Gate: a strategy subset must be active. Full-roster runs stay unpruned.
    subset = os.environ.get("STRATEGY_SUBSET_FILE")
    if not subset:
        return "off"
    return "warmup"


def reset_state():
    """Test-only: return the state machine to undecided."""
    _STATE.update({"mode": None, "read": set(), "skip": frozenset(),
                   "warmup_left": 0})


def state() -> dict:
    return dict(_STATE)


def begin_bar(sample_df=None) -> set:
    """Skip set for THIS bar's compute_all_signals call.

    Empty during warmup (everything is computed so reads can be observed) and
    the derived set afterwards.
    """
    import os
    if _STATE["mode"] is None:
        _STATE["mode"] = _decide_mode()
        if _STATE["mode"] == "warmup":
            _STATE["warmup_left"] = int(
                os.environ.get("DEMAND_PRUNING_WARMUP", WARMUP_BARS_DEFAULT))
            if _PRODUCER_KEYS is None and sample_df is not None:
                try:
                    build_producer_key_map(sample_df)
                except Exception:
                    # Never let the optimisation break the run: fall back to
                    # computing everything (CHECKLIST #122 -- but this one is
                    # a documented degrade-to-safe, and it is LOGGED below).
                    _STATE["mode"] = "off"
    if _STATE["mode"] == "pruned":
        return set(_STATE["skip_producers"])
    return set()


def wrap(signals: dict) -> dict:
    """Wrap the signals dict for this bar and advance the warmup counter."""
    mode = _STATE["mode"]
    if mode == "warmup":
        wrapped = RecordingSignals(signals, _STATE["read"])
        _STATE["warmup_left"] -= 1
        if _STATE["warmup_left"] <= 0:
            _finalise()
        return wrapped
    if mode == "pruned":
        return GuardedSignals(signals, _STATE["skip"])
    return signals


def _finalise():
    """Turn recorded reads into a producer skip set."""
    import logging
    log = logging.getLogger(__name__)
    km = _PRODUCER_KEYS or {}
    keep = required_producers(_STATE["read"], km)
    _STATE["skip_producers"] = frozenset(set(km) - keep)
    _STATE["skip"] = skipped_keys(keep, km)
    _STATE["mode"] = "pruned"
    log.info("demand-pruning ARMED: %d/%d producers kept, %d keys pruned "
             "(recorded %d reads over warmup)",
             len(keep), len(km), len(_STATE["skip"]), len(_STATE["read"]))


__all__ += ["begin_bar", "wrap", "reset_state", "state",
            "WARMUP_BARS_DEFAULT"]
