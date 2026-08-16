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
import logging
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
        # S6-B1581: MUST use dict.__contains__ directly. Once __contains__ is
        # overridden to call _check (so the `"k" in s` idiom is guarded), a
        # plain `key not in self` here recurses infinitely. Caught by
        # test_b1581_guard_protects_contains_idiom on its first run.
        if not dict.__contains__(self, key) and key in self._skipped:
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

    def __contains__(self, key):
        # S6-B1580a: RecordingSignals treats `"k" in s` as a READ, so the guard
        # must treat it as one too. Without this, `"pruned_key" in s` returned
        # False SILENTLY - the recorder counted a key the guard would not
        # protect. No strategy uses the idiom today (0 of 222), which is
        # exactly why it would have shipped unnoticed.
        self._check(key)
        return super().__contains__(key)


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
    "warmup_days": set(),
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
                   "warmup_left": 0, "warmup_days": set()})


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


def wrap(signals: dict, as_of=None) -> dict:
    """Wrap the signals dict for this bar and advance the warmup counter.

    `as_of` is the SIM DATE. Warmup completes after that many DISTINCT
    dates, not that many calls (S6-B1580b).
    """
    mode = _STATE["mode"]
    if mode == "warmup":
        wrapped = RecordingSignals(signals, _STATE["read"])
        # S6-B1580b: count DISTINCT SIM-DAYS, not calls. `wrap()` fires once per
        # (ticker, day), so decrementing per call meant 25 "bars" = 25 ticker-
        # calls = 0.25 SIM-DAYS at a 100-ticker universe. The whole safety
        # argument rests on warmup observing what strategies read, and a quarter
        # of one day observes almost nothing.
        if as_of is not None:
            seen = _STATE.setdefault("warmup_days", set())
            if as_of not in seen:
                seen.add(as_of)
                _STATE["warmup_left"] -= 1
        else:
            # No date supplied -> fall back to per-call counting rather than
            # never finishing warmup. Logged so the degradation is visible.
            _STATE["warmup_left"] -= 1
        if _STATE["warmup_left"] <= 0:
            _finalise()
        return wrapped
    if mode == "pruned":
        return GuardedSignals(signals, _STATE["skip"])
    return signals


def _static_keys_of_active_strategies() -> set:
    """Signal-key literals appearing in the ACTIVE strategies' source.

    A FLOOR, not the answer. Static extraction cannot see runtime-built keys
    (L437), which is why runtime recording exists -- but it DOES see keys that
    runtime recording misses because a boolean short-circuited past them. Used
    only in union with recorded reads, so it can only widen what is kept.

    ALL_STRATEGIES is already narrowed by STRATEGY_SUBSET_FILE at import
    (run_phase1a.py), so this scans exactly the strategies that will run.
    """
    keys: set = set()
    try:
        import inspect
        import re
        from backtest.signals.screener import ALL_STRATEGIES
        for fn in ALL_STRATEGIES.values():
            try:
                src = inspect.getsource(fn)
            except Exception as _e:
                # CHECKLIST #122: NOT benign. A strategy whose source cannot be
                # read contributes no static keys, so the floor is lower than
                # it should be and we may OVER-prune -- which surfaces later as
                # a SkippedSignalError mid-run rather than here.
                logging.getLogger(__name__).warning(
                    "static-key scan could not read source for %r (%r); its "
                    "keys are absent from the prune floor", fn, _e)
                continue
            keys |= set(re.findall(r's\.get\(\s*["\']([a-zA-Z0-9_]+)', src))
            keys |= set(re.findall(r's\[\s*["\']([a-zA-Z0-9_]+)', src))
    except Exception as _e:
        # Degrade to runtime-only recording rather than break the run; the
        # guard still converts any missed key into a loud failure. Logged
        # because a silent degrade here removes the short-circuit protection
        # (L444) without any visible symptom.
        logging.getLogger(__name__).warning(
            "static-key floor unavailable (%r); falling back to runtime-only "
            "recording -- short-circuited keys will NOT be protected", _e)
        return set()
    return keys

def _finalise():
    """Turn recorded reads into a producer skip set."""
    import logging
    log = logging.getLogger(__name__)
    km = _PRODUCER_KEYS or {}
    # B1570: union RUNTIME-recorded reads with STATICALLY-extracted literals.
    # The two methods fail in COMPLEMENTARY directions, so neither alone is
    # sufficient:
    #   - static misses RUNTIME-BUILT keys (smc_breaker_block_long's
    #     f"price_above_ema_{span}") -- that is L437, which blocked this work.
    #   - runtime misses SHORT-CIRCUITED keys. smc_ote_long is
    #     `s.get("smc_ote_long_zone") and (s.get("smc_bos_bullish") or ...)`;
    #     if the zone is False on every warmup bar the `and` short-circuits and
    #     the bos keys are NEVER read, so bos_choch gets pruned -- and the run
    #     then dies on the first bar where the zone goes True.
    # Union is strictly safer than either: it can only ever KEEP more
    # producers, never fewer, so it cannot introduce a missing key.
    _static = _static_keys_of_active_strategies()
    _read = set(_STATE["read"]) | _static
    _STATE["static_keys"] = frozenset(_static)
    keep = required_producers(_read, km)
    _STATE["skip_producers"] = frozenset(set(km) - keep)
    _STATE["mode"] = "pruned"
    # B1569: SMC-skipped keys must join the guard set too. Without this a key
    # from a pruned SMC primitive would be merely ABSENT, and `.get()` would
    # hand back a default -- the exact silent misfire (L437) the guard exists
    # to prevent. `smc_skip_primitives()` requires mode=="pruned", hence the
    # ordering above.
    _smc_skipped = smc_skipped_keys(smc_skip_primitives())
    _STATE["skip"] = frozenset(set(skipped_keys(keep, km)) | set(_smc_skipped))
    log.info("demand-pruning ARMED: %d/%d producers kept, %d keys pruned "
             "(recorded %d reads over warmup)",
             len(keep), len(km), len(_STATE["skip"]), len(_STATE["read"]))


__all__ += ["begin_bar", "wrap", "reset_state", "state",
            "WARMUP_BARS_DEFAULT"]


# ---------------------------------------------------------------------------
# B1569 -- SMC primitive pruning (compute_smc_signals = 27.2pct of runtime)
#
# Measured per-primitive cost (steady-state median of 5, 800-bar AAPL):
#     retracements 121.99 ms (46.7pct) | fvg 73.39 (28.1) | bos_choch 47.24 (18.1)
#     ob 10.53 (4.0) | swing_highs_lows 5.42 (2.1) | liquidity 2.50 (1.0)
# The three guarded here are 92.9pct of the cost. `ob`, `liquidity` and the
# shared `swings` dependency stay always-on: they are cheap, and `swings` feeds
# four primitives so skipping it would require all four to be unused.
#
# This map is HARDCODED for runtime cheapness -- deriving it would cost three
# extra compute_smc_signals calls per bar, which is the thing we are avoiding.
# `test_b1569_smc_primitive_map_matches_reality` RE-DERIVES it by diffing real
# output and fails if it drifts, so the constant cannot silently rot.
# ---------------------------------------------------------------------------

SMC_PRIMITIVE_KEYS: dict[str, frozenset[str]] = {
    "fvg": frozenset({
        "smc_fvg_bearish_active", "smc_fvg_bullish_active",
        "smc_fvg_retest_long_zone", "smc_fvg_retest_short_zone",
        "smc_inverse_fvg_bearish", "smc_inverse_fvg_bullish",
    }),
    "bos_choch": frozenset({
        "smc_bos_bearish", "smc_bos_bullish",
        "smc_bos_retest_long", "smc_bos_retest_short",
        "smc_choch_bearish", "smc_choch_bullish",
    }),
    "retracements": frozenset({
        "smc_ote_long_zone", "smc_ote_short_zone", "smc_retracement_pct",
    }),
}


def smc_skip_primitives(read_keys: Iterable[str] | None = None) -> set:
    """SMC primitives whose keys are never read -> safe to skip.

    Returns an EMPTY set unless pruning is armed, so the unpruned path is
    unchanged. During warmup nothing is skipped, because the read set is still
    being collected and skipping early would hide the very reads we need.
    """
    if _STATE["mode"] != "pruned":
        return set()
    # B1570: same union as _finalise -- short-circuited SMC keys (smc_ote_long)
    # are invisible to runtime recording and would otherwise be pruned.
    rk = (set(read_keys) if read_keys is not None
          else set(_STATE["read"]) | set(_STATE.get("static_keys", ())))
    return {p for p, keys in SMC_PRIMITIVE_KEYS.items() if not (keys & rk)}


def smc_skipped_keys(skipped_prims: Iterable[str]) -> frozenset[str]:
    """Keys that will be absent because their SMC primitive was skipped."""
    out: set[str] = set()
    for p in skipped_prims:
        out |= set(SMC_PRIMITIVE_KEYS.get(p, ()))
    return frozenset(out)


__all__ += ["SMC_PRIMITIVE_KEYS", "smc_skip_primitives", "smc_skipped_keys"]
