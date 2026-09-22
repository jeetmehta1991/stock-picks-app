#!/usr/bin/env python
"""HELD PATCH - S6-B2931 (owner ruled 2026-09-22: SPLIT BOTH).

APPLY AT CHAIN DONE ONLY. backtest/signals/screener.py defines
ALL_STRATEGIES, imported at engine start by run_phase1a.py:31 - editing it
mid-chain puts configs on different rosters (S6-B2957 / L836 addendum).
The chain-done checklist runs:

    python output_audit/held_patches/b2931_split_patch.py
    python -m pytest backtest/tests/test_unit.py -q -k "b2931 or f_002 or 15457"
    python scripts/build_strategy_status.py     # regenerate the 223-row doc
    python scripts/drift_audit_pre_phase_1a_beta.py   # snapshot strategy_total
                       # 223 -> 225 (worktree validation 2026-09-22 found
                       # test_batch373_e1_drift reading this snapshot; with it
                       # regenerated, 7 of 7 targeted pins pass)
    python scripts/pyramid_gate.py --out output_audit/b2931_apply_gate.json \
        -- backtest/tests/test_unit.py backtest/tests/test_integration.py -q

THE RULING AND ITS SHAPE. B1202 (Council 278) added smc_bos_bearish as an
OR-alternative inside turtle_soup_short and smc_equal_highs_sweep_short.
The S6-B2931 attribution artifacts measured that the added arm carries the
MAJORITY of one strategy's fires and a large share of the other's, so one
NAME covers two trade populations and the roster misdescribes itself. The
owner ruled SPLIT BOTH ('1 to 4 approve your recs' item 3, 2026-09-22).

THE PARTITION IS EXACT, by construction: the thesis strategy keeps its
pre-B1202 gate (sweep signal only); the new *_bos_* strategy fires on
bos AND NOT the sweep signal. Union of the two == the current OR, and no
bar fires in both - total fires are preserved, only the naming splits.
Both new registrations keep the parent's family and the parent's other
confluence gates verbatim, and their docstrings carry the lineage.

COUNT PINS moved 223 -> 225 (and derived counts +2) at the FOUR sites this
file edits by exact anchor; a fifth pin (the status doc's 223 rows) moves
by REGENERATION, not by edit - run build_strategy_status.py as listed.
CLAUDE.md's canonical counts are banner-synced in the applying commit.
"""
import ast
import io
import sys

def rd(p):
    return io.open(p, encoding="utf-8", newline="").read()

def nl(p):
    return "\r\n" if "\r\n" in rd(p) else "\n"

def sub(path, old, new, count=1):
    s = rd(path)
    n = s.count(old)
    assert n == count, "anchor in %s occurs %d (want %d): %r" % (
        path, n, count, old[:70])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new))
    print("  patched", path)

SC = "backtest/signals/screener.py"
T = "backtest/tests/test_unit.py"


def apply() -> int:
    N = nl(SC)

    # ---- 1. turtle_soup_short: thesis-only again ------------------------
    sub(SC,
        "    fires = (" + N +
        "        (s.get(\"smc_liquidity_swept_up\", False) or s.get(\"smc_bos_bearish\", False))" + N +
        "        and s.get(\"below_prev_high\", False)     # B616: closed back BELOW prior-day-high" + N +
        "        and s.get(\"close_below_open\", False)    # bearish reversal bar" + N +
        "     and not _short_borrow_trap_active(s))" + N +
        "    return _strat(fires, \"short\", \"ict\"," + N +
        "        [\"(smc_liquidity_swept_up OR smc_bos_bearish)\", \"below_prev_high\", \"close_below_open\", \"borrow_ok\"],",
        "    # S6-B2931 (owner ruled 2026-09-22 SPLIT): thesis arm only -" + N +
        "    # the B1202 smc_bos_bearish OR-arm now lives in" + N +
        "    # strat_turtle_soup_bos_short, so one name covers one population." + N +
        "    fires = (" + N +
        "        s.get(\"smc_liquidity_swept_up\", False)" + N +
        "        and s.get(\"below_prev_high\", False)     # B616: closed back BELOW prior-day-high" + N +
        "        and s.get(\"close_below_open\", False)    # bearish reversal bar" + N +
        "     and not _short_borrow_trap_active(s))" + N +
        "    return _strat(fires, \"short\", \"ict\"," + N +
        "        [\"smc_liquidity_swept_up\", \"below_prev_high\", \"close_below_open\", \"borrow_ok\"],")

    # ---- 2. the new turtle bos registration, directly after the parent --
    sub(SC,
        "         \"Bearish close below open - rejection of upside breakout\"])",
        "         \"Bearish close below open - rejection of upside breakout\"])" + N +
        N + N +
        "def strat_turtle_soup_bos_short(s):" + N +
        "    \"\"\"S6-B2931 (owner ruled 2026-09-22): the B1202-added arm of" + N +
        "    turtle_soup_short as its own registration. B1202 (Council 278)" + N +
        "    added smc_bos_bearish as an OR-alternative; the S6-B2931" + N +
        "    attribution artifacts measured that arm carrying the majority of" + N +
        "    the name's fires - two populations under one name. The partition" + N +
        "    is exact: this fires on bos AND NOT the sweep signal, the parent" + N +
        "    keeps the sweep signal, union == the pre-split OR.\"\"\"" + N +
        "    fires = (" + N +
        "        s.get(\"smc_bos_bearish\", False)" + N +
        "        and not s.get(\"smc_liquidity_swept_up\", False)  # exact partition" + N +
        "        and s.get(\"below_prev_high\", False)" + N +
        "        and s.get(\"close_below_open\", False)" + N +
        "     and not _short_borrow_trap_active(s))" + N +
        "    return _strat(fires, \"short\", \"ict\"," + N +
        "        [\"smc_bos_bearish AND NOT smc_liquidity_swept_up\"," + N +
        "         \"below_prev_high\", \"close_below_open\", \"borrow_ok\"]," + N +
        "        [\"Turtle Soup bos-arm short (S6-B2931 split of the B1202 add)\"," + N +
        "         \"Bearish break-of-structure without a liquidity sweep\"," + N +
        "         \"Price reversed back BELOW prior-day-high\"," + N +
        "         \"Bearish close below open\"])")

    # ---- 3. smc_equal_highs_sweep_short: thesis-only again --------------
    sub(SC,
        "    fires = (" + N +
        "        (s.get(\"smc_equal_highs_swept\", False) or s.get(\"smc_bos_bearish\", False))" + N +
        "        and s.get(\"smc_fvg_bearish_active\", False)" + N +
        "     and not _short_borrow_trap_active(s))" + N +
        "    return _strat(fires, \"short\", \"smc\"," + N +
        "        [\"(smc_equal_highs_swept OR smc_bos_bearish)\", \"smc_fvg_bearish_active\", \"borrow_ok\"],",
        "    # S6-B2931 (owner ruled 2026-09-22 SPLIT): thesis arm only - the" + N +
        "    # B1202 OR-arm now lives in strat_smc_equal_highs_bos_short." + N +
        "    fires = (" + N +
        "        s.get(\"smc_equal_highs_swept\", False)" + N +
        "        and s.get(\"smc_fvg_bearish_active\", False)" + N +
        "     and not _short_borrow_trap_active(s))" + N +
        "    return _strat(fires, \"short\", \"smc\"," + N +
        "        [\"smc_equal_highs_swept\", \"smc_fvg_bearish_active\", \"borrow_ok\"],")

    # ---- 4. the new equal-highs bos registration ------------------------
    sub(SC,
        "         \"Bearish FVG active below - reversal confluence\"])",
        "         \"Bearish FVG active below - reversal confluence\"])" + N +
        N + N +
        "def strat_smc_equal_highs_bos_short(s):" + N +
        "    \"\"\"S6-B2931 (owner ruled 2026-09-22): the B1202-added arm of" + N +
        "    smc_equal_highs_sweep_short as its own registration; exact" + N +
        "    partition (bos AND NOT swept), union == the pre-split OR.\"\"\"" + N +
        "    fires = (" + N +
        "        s.get(\"smc_bos_bearish\", False)" + N +
        "        and not s.get(\"smc_equal_highs_swept\", False)  # exact partition" + N +
        "        and s.get(\"smc_fvg_bearish_active\", False)" + N +
        "     and not _short_borrow_trap_active(s))" + N +
        "    return _strat(fires, \"short\", \"smc\"," + N +
        "        [\"smc_bos_bearish AND NOT smc_equal_highs_swept\"," + N +
        "         \"smc_fvg_bearish_active\", \"borrow_ok\"]," + N +
        "        [\"Equal-highs bos-arm short (S6-B2931 split of the B1202 add)\"," + N +
        "         \"Bearish FVG active below - reversal confluence\"])")

    # ---- 5. dict registrations, each after its parent's entry -----------
    sub(SC,
        "    \"turtle_soup_short\":            strat_turtle_soup_short,",
        "    \"turtle_soup_short\":            strat_turtle_soup_short," + N +
        "    # S6-B2931 split (owner ruled 2026-09-22): the B1202 bos arm" + N +
        "    \"turtle_soup_bos_short\":        strat_turtle_soup_bos_short,")
    sub(SC,
        "    \"smc_equal_highs_sweep_short\":  strat_smc_equal_highs_sweep_short,",
        "    \"smc_equal_highs_sweep_short\":  strat_smc_equal_highs_sweep_short," + N +
        "    # S6-B2931 split (owner ruled 2026-09-22): the B1202 bos arm" + N +
        "    \"smc_equal_highs_bos_short\":    strat_smc_equal_highs_bos_short,")

    ast.parse(rd(SC))
    print("  screener split applied - AST OK")

    # ---- 6. the four count pins, by exact anchor ------------------------
    TN = nl(T)
    sub(T,
        "    # B2680: 221 -> 223 (+2 owner-worded vwap-extension pair)." + TN +
        "    assert len(ALL_STRATEGIES) == 223, (" + TN +
        "        f\"F-002 drift: ALL_STRATEGIES expected 223 post-B2680 (221 \"" + TN +
        "        f\"post-B2669); got {len(ALL_STRATEGIES)}. \"",
        "    # B2680: 221 -> 223 (+2 owner-worded vwap-extension pair)." + TN +
        "    # S6-B2931: 223 -> 225 (+2 owner-ruled splits of the B1202 arm:" + TN +
        "    # turtle_soup_bos_short, smc_equal_highs_bos_short)." + TN +
        "    assert len(ALL_STRATEGIES) == 225, (" + TN +
        "        f\"F-002 drift: ALL_STRATEGIES expected 225 post-B2931 (223 \"" + TN +
        "        f\"post-B2680); got {len(ALL_STRATEGIES)}. \"")
    sub(T,
        "    assert active == 223, (" + TN +
        "        f\"F-002 drift: active strategy count expected 223 (223 registered \"" + TN +
        "        f\"post-B2680); got {active}.\"",
        "    assert active == 225, (" + TN +
        "        f\"F-002 drift: active strategy count expected 225 (225 registered \"" + TN +
        "        f\"post-B2931); got {active}.\"")
    sub(T,
        "    assert len(set(ALL_STRATEGIES) - DS - MP - DEP) == 222, (" + TN +
        "        \"active count drifted from 222 (223 registered post-B2680 minus the \"" + TN +
        "        \"data-scarce survivor)\")",
        "    assert len(set(ALL_STRATEGIES) - DS - MP - DEP) == 224, (" + TN +
        "        \"active count drifted from 224 (225 registered post-B2931 minus the \"" + TN +
        "        \"data-scarce survivor)\")")
    sub(T,
        "    assert len(ALL_STRATEGIES) == 223, (" + TN +
        "        f\"roster is {len(ALL_STRATEGIES)}; the variant factory must not \"" + TN +
        "        f\"register anything until an admission is owner-approved\")",
        "    assert len(ALL_STRATEGIES) == 225, (" + TN +
        "        f\"roster is {len(ALL_STRATEGIES)}; the variant factory must not \"" + TN +
        "        f\"register anything until an admission is owner-approved\")")
    # the fifth pin (status-doc rows == 223 at test_unit.py:38334) moves by
    # REGENERATING the doc; after build_strategy_status.py the row count is
    # 225 and this edit keeps the assert in step:
    sub(T,
        "    assert sum(st.values()) == len(rows) == 223",
        "    assert sum(st.values()) == len(rows) == 225")

    # ---- 7. the pin for the split itself --------------------------------
    TEST = '''


def test_b2931_split_is_an_exact_partition():
    """S6-B2931 (owner ruled 2026-09-22): the B1202 OR-arm is its own
    registration and the split PARTITIONS the old OR exactly - no bar
    fires in both, and every bar the old OR admitted fires in exactly one.
    """
    from backtest.signals.screener import (
        ALL_STRATEGIES, strat_turtle_soup_short, strat_turtle_soup_bos_short,
        strat_smc_equal_highs_sweep_short, strat_smc_equal_highs_bos_short)

    assert "turtle_soup_bos_short" in ALL_STRATEGIES
    assert "smc_equal_highs_bos_short" in ALL_STRATEGIES

    base = {"below_prev_high": True, "close_below_open": True,
            "smc_fvg_bearish_active": True, "borrow_ok": True}

    # sweep-only bar: thesis fires, bos-arm does not
    s1 = dict(base, smc_liquidity_swept_up=True, smc_bos_bearish=False,
              smc_equal_highs_swept=True)
    assert strat_turtle_soup_short(s1)["fires"]
    assert not strat_turtle_soup_bos_short(s1)["fires"]
    assert strat_smc_equal_highs_sweep_short(s1)["fires"]
    assert not strat_smc_equal_highs_bos_short(s1)["fires"]

    # bos-only bar: bos-arm fires, thesis does not
    s2 = dict(base, smc_liquidity_swept_up=False, smc_bos_bearish=True,
              smc_equal_highs_swept=False)
    assert not strat_turtle_soup_short(s2)["fires"]
    assert strat_turtle_soup_bos_short(s2)["fires"]
    assert not strat_smc_equal_highs_sweep_short(s2)["fires"]
    assert strat_smc_equal_highs_bos_short(s2)["fires"]

    # both-signals bar: thesis wins, bos-arm stays quiet (exact partition,
    # matching the attribution artifacts' thesis_only/both/added_only split)
    s3 = dict(base, smc_liquidity_swept_up=True, smc_bos_bearish=True,
              smc_equal_highs_swept=True)
    assert strat_turtle_soup_short(s3)["fires"]
    assert not strat_turtle_soup_bos_short(s3)["fires"]
    assert strat_smc_equal_highs_sweep_short(s3)["fires"]
    assert not strat_smc_equal_highs_bos_short(s3)["fires"]

    # neither-signal bar: all four quiet
    s4 = dict(base, smc_liquidity_swept_up=False, smc_bos_bearish=False,
              smc_equal_highs_swept=False)
    for f in (strat_turtle_soup_short, strat_turtle_soup_bos_short,
              strat_smc_equal_highs_sweep_short,
              strat_smc_equal_highs_bos_short):
        assert not f(s4)["fires"]
'''
    raw = rd(T)
    assert "test_b2931_split_is_an_exact_partition" not in raw
    io.open(T, "a", encoding="utf-8", newline="").write(
        TEST.replace("\n", TN) if TN != "\n" else TEST)
    ast.parse(rd(T))
    print("  count pins moved and the partition pin appended - AST OK")
    print("S6-B2931 SPLIT APPLIED - regenerate the status doc, banner-sync "
          "CLAUDE.md, then run the pyramid gate before committing")
    return 0


if __name__ == "__main__":
    sys.exit(apply())
