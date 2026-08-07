# Source: Decision 5 Cat 1 critical path + B713 Phase 0 + owner-approved Option A "option a" 2026-06-13 per CHECKLIST #77
"""B743 pin tests: dual `_strat3` second chunk -- remaining 30 of 61 dual
strategies converted to explicit `borrow_ok` borrow gate on the SHORT branch.

Combined with B740 + B741 + B742, ALL 112 short-emitting strategies (51 pure-short
+ 61 dual _strat3) now declare borrow_ok at call site + carry explicit
`_short_borrow_trap_active(s)` gate. B736 registration-time borrow-gate lint
is now fully unblocked.

Includes a cluster-wide invariant: scan screener.py and assert every function
body whose return path contains `_strat3` AND mentions `direction="short"`
output path also contains `_short_borrow_trap_active(s)`.
"""
from __future__ import annotations

from backtest.signals.screener import ALL_STRATEGIES

B743_STRATEGIES = [
    "bollinger_lower",
    "bollinger_tight",
    "keltner_lower",
    "stoch_oversold",
    "volume_spike_breakout",
    "force_index_breakout",
    "donchian_10_breakout",
    "morning_star",
    "bullish_engulfing_support",
    "rsi_volume_200ema",
    "macd_ichimoku",
    "bb_squeeze_volume",
    "pivot_fib_confluence",
    "golden_cross_volume",
    "cpr_narrow_momentum",
    # camarilla_rsi_obv DELETED B874 per S4-B754-A-19 Pattern W council
    # 5-lens option A2 (literal-duplicate-pair META-PATTERN with standalone
    # SHORT). Removed from B718b strat3 cohort B899 migration.
    "supertrend_ichimoku_adx",
    "williams_stoch_dual",
    "dc20_break_retest",
    "r1_break_retest",
    "break_retest_volume",
    "break_retest_confluence",
    "smc_inverse_fvg",
    "smc_bos_retest_entry",
    "smc_bos_continuation",
    "smc_choch_reversal",
    "smc_order_block_bounce",
    "smc_liquidity_sweep_reversal",
    "avwap_252_breakout",
    "avwap_50_reclaim",
]


def test_b743_pin1_count_matches_29():
    # B899 migration: 30 -> 29 post-B874 deletion of camarilla_rsi_obv (dual).
    assert len(B743_STRATEGIES) == 29


def test_b743_pin2_all_30_registered():
    missing = [s for s in B743_STRATEGIES if s not in ALL_STRATEGIES]
    assert not missing, f"missing: {missing}"


def test_b743_pin3_combined_strat3_count_is_60():
    """B742 (31) + B743 (29 post-B874) = 59 total dual `_strat3` strategies.
    Was 61 at B743 time; B899 migration post-B874 deletion of camarilla_rsi_obv;
    B1465 (owner-approved S6-B1463a) 60 -> 59: prev_day_high_break converted from
    _strat3 to _strat because its SHORT branch was character-identical to standalone
    prev_day_low_breakdown (jaccard 0.9850, a strict subset). It is genuinely long-only
    now, so a dual-strategy pin no longer applies to it.

    Cluster-wide regression guard: if a new dual strategy is added later,
    this test fails and the author is forced to add it to either cohort
    AND give it explicit gate per the S4-B713 discipline.
    """
    import re
    src = open("backtest/signals/screener.py", encoding="utf-8").read()
    strat3_count = len(re.findall(r'return _strat3\(', src))
    expected = 59  # B1465: 60 -> 59, prev_day_high_break _strat3 -> _strat (long-only)
    assert strat3_count == expected, (
        f"expected {expected} dual _strat3 strategies; got {strat3_count}. "
        f"If a new dual strategy was added, it must be added to either B742 or B743 cohort "
        f"+ given explicit borrow_ok gate on its SHORT branch per S4-B713-INSPECT-CURRENTFRAME-REVERT."
    )


def test_b743_pin4_every_strat3_function_carries_explicit_short_gate():
    """Cluster-wide regression: every function body ending with `return _strat3(...)`
    must contain `_short_borrow_trap_active(s)` (the explicit short-branch gate).

    B718d removal of inspect.currentframe from _strat3 helper relies on this
    invariant holding for all dual strategies.
    """
    import re
    src = open("backtest/signals/screener.py", encoding="utf-8").read()
    lines = src.splitlines()
    missing_gate = []
    in_function = None
    function_start = None
    for i, line in enumerate(lines):
        m = re.match(r"^def (strat_\w+)\(s\):\s*$", line)
        if m:
            in_function = m.group(1)
            function_start = i
            continue
        if in_function is None:
            continue
        if "return _strat3(" in line:
            body = "\n".join(lines[function_start:i + 1])
            if "_short_borrow_trap_active(s)" not in body:
                missing_gate.append(in_function)
            in_function = None
            function_start = None
            continue
    assert not missing_gate, (
        f"dual _strat3 strategies missing explicit SHORT gate: {missing_gate}"
    )


def test_b743_pin5_short_branch_declares_borrow_ok_when_fires():
    s = _permissive_bearish_dict()
    found = []
    for name in B743_STRATEGIES:
        r = ALL_STRATEGIES[name](s)
        if r["fires"] and r["direction"] == "short":
            assert "borrow_ok" in r["signals_used"], (
                f"{name} fired SHORT but signals_used missing borrow_ok: {r['signals_used']}"
            )
            found.append(name)
    assert found, "expected >=1 SHORT fire under permissive bearish signals"


def test_b743_pin6_borrow_trap_blocks_short_branch():
    s = _permissive_bearish_dict()
    s["days_to_cover"] = 10.0
    leaks = [n for n in B743_STRATEGIES if ALL_STRATEGIES[n](s)["fires"] and ALL_STRATEGIES[n](s)["direction"] == "short"]
    assert not leaks, f"borrow trap should block SHORT but these fired: {leaks}"


def test_b743_pin7_long_branch_unaffected_by_borrow_trap():
    """LONG branch fires under high DTC -- gate is SHORT-only."""
    s = _permissive_bullish_dict()
    s["days_to_cover"] = 10.0
    longs = [
        n for n in B743_STRATEGIES
        if ALL_STRATEGIES[n](s)["fires"] and ALL_STRATEGIES[n](s)["direction"] == "long"
    ]
    assert longs, "expected >=1 LONG fire despite DTC=10 (gate is SHORT-only)"


# --------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# B1471 (S6-B1467b) -- FIXTURES DERIVED FROM THE STRATEGIES, NOT HAND-MAINTAINED.
#
# The previous fixtures were literal dicts of ~55 keys. They had drifted so far
# from the strategies' current gates that NOTHING fired under them: pin5 ("expect
# >=1 SHORT fire") and pin7 ("expect >=1 LONG fire") failed on empty lists, and had
# been failing for an unknown span because this file is outside the enforced 2-file
# gate (L310/L312). A stale fixture does not fail loudly -- it asserts nothing and
# still reports red, so it reads as a broken test rather than a broken fixture.
#
# Root cause is that the fixture duplicated knowledge the strategies already hold.
# Every gate change (B722 STATE->EVENT, B1139/B1194/B1197 loosening, B1465 disables)
# silently invalidated it. These build the dicts BY PARSING the strategies' own
# `fl =` and `fs =` expressions, so the fixture cannot drift from what it tests:
# add a gate to a strategy and the fixture grows the key on the next run.
#
# Side assignment matters: setting every key True makes both branches fire at once
# and `_strat3` resolves the conflict to direction "avoid" (measured: 21 of 29), so
# the long-side keys are set False in the bearish dict and vice versa.
# ---------------------------------------------------------------------------

def _side_keys() -> tuple[set, set]:
    """(long-side keys, short-side keys) across B743_STRATEGIES, read from source."""
    import inspect
    import re as _re
    long_k, short_k = set(), set()
    for name in B743_STRATEGIES:
        src = inspect.getsource(ALL_STRATEGIES[name])
        fl = _re.search(r"^\s*fl\s*=(.*?)(?=^\s*fs\s*=)", src, _re.S | _re.M)
        fs = _re.search(r"^\s*fs\s*=(.*?)(?=^\s*return)", src, _re.S | _re.M)
        if fl:
            long_k |= set(_re.findall(r's\.get\("([a-z0-9_]+)"', fl.group(1)))
        if fs:
            short_k |= set(_re.findall(r's\.get\("([a-z0-9_]+)"', fs.group(1)))
    return long_k, short_k


def _permissive_bearish_dict() -> dict:
    """Short-side gates True, long-side False, borrow trap OFF."""
    long_k, short_k = _side_keys()
    d = {k: False for k in long_k}
    d.update({k: True for k in short_k})
    d["days_to_cover"] = 0.0
    return d


def _permissive_bullish_dict() -> dict:
    """Long-side gates True, short-side False, borrow trap OFF."""
    long_k, short_k = _side_keys()
    d = {k: False for k in short_k}
    d.update({k: True for k in long_k})
    d["days_to_cover"] = 0.0
    return d
