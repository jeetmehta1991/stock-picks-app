#!/usr/bin/env python
"""HELD PATCH - S6-B3037 OPTION B (owner ruled RE-DERIVE 2026-09-23).

Source: this file. It edits scripts/or_arm_attribution.py and
backtest/tests/test_unit.py by exact anchor and stores nothing.

*** APPLIES ONLY AFTER b2931_split_patch.py HAS LANDED. ***
The owner's ruling was RE-DERIVE, not retire: test_b1248 stays as the check
coupling or_arm_attribution.GATES to the live screener, and both it and the
script are re-pointed so they describe the POST-SPLIT code.

WHAT RE-DERIVE MEANS HERE, AND WHY IT IS NOT A RENAME.

  The script classifies every landed trade of a strategy by which arm was
  true in signals_at_entry. Before the split that is informative: a trade
  can rest on the thesis arm, the B1202 arm, or both.

  AFTER the split it goes DEGENERATE BY CONSTRUCTION, and re-pointing GATES
  at the new names without saying so would publish 0 pct and 100 pct as if
  they were measurements. DERIVED from the b2931 patch source, not measured,
  because no post-split cube exists yet: the parent fires only when the
  thesis signal is true, so added_only is 0 and thesis_only + both is the
  whole readable population; the bos registration fires only when the added
  signal is true AND the thesis signal is false, so added_only is the whole
  population. Those are properties of the gates, not of the data.

  So the re-derivation is three things:
    1. GATES gains the two new registrations, each carrying its parent's
       signal pair, so the script runs on post-split cubes at all.
    2. SPLIT_PAIRS records which bos registration belongs to which parent -
       the pair is now the unit of analysis, because the question "how much
       of this name rests on the added arm" is answered by the pair's two
       populations rather than by one name's internal split.
    3. Every emitted row carries a REGIME field, so a reader can tell a
       measured share from a structural one. A number that cannot be wrong
       is not evidence, and labelling it is the whole point.

  OLD CUBES STAY INFORMATIVE. A cube written before the split carries the
  pre-split strategy names, so the parents' rows keep their real
  thesis/both/added split - output_r5_merged_1_7 gave 838 landed splitting
  2 / 304 / 532 / 0 and 1880 splitting 58 / 253 / 1569 / 0 at S6-B3043.
  This patch does not touch that artifact.

WHAT test_b1248 BECOMES. It asserted `" or " in body` - that the OR gate is
still there - which the split deliberately removes. Re-derived, it asserts
the PARTITION and the PAIRING, which is the same coupling claim against the
new code: each parent still carries its thesis signal and NO LONGER calls
s.get on the added one; each bos registration calls s.get on the added
signal AND negates the thesis signal. That negation is what makes the two
registrations disjoint, so it is the assertion worth having.

  NOTE ON THE ANCHOR, because the obvious version is wrong: b2931 writes
  "the B1202 smc_bos_bearish OR-arm now lives in ..." into the PARENT's
  comment, so a bare `added not in body` check would match prose and pass
  while testing nothing (L748). The assertions below anchor on the
  executable form s.get("<signal>" instead.

APPLY CHECKLIST (after b2931, at CHAIN DONE):

    python output_audit/held_patches/b3037b_rederive_or_arm_attribution.py
    python -m pytest backtest/tests/test_unit.py -q -k "b1248 or b2931"
    #   #315: names the pin this change REWRITES (b1248) and the pin whose
    #   partition it now leans on (b2931). Both move together or neither.
    python scripts/or_arm_attribution.py --cube output_r5_merged_1_7
    #   re-run on the PRE-split cube: the parents' rows must be unchanged
    #   from S6-B3043 and must now carry regime PRE_SPLIT_INFORMATIVE.
    python scripts/pyramid_gate.py --out output_audit/b3037b_apply_gate.json \\
        -- backtest/tests/test_unit.py backtest/tests/test_integration.py -q
"""
import ast
import io
import sys

S = "scripts/or_arm_attribution.py"
T = "backtest/tests/test_unit.py"


def rd(p):
    return io.open(p, encoding="utf-8", newline="").read()


def nl(p):
    text = rd(p)
    return "\r\n" if text.count("\r\n") * 2 > text.count("\n") else "\n"


def sub(path, old, new, count=1):
    s = rd(path)
    n = s.count(old)
    assert n == count, "anchor in %s occurs %d (want %d): %r" % (
        path, n, count, old[:70])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new))
    print("  patched", path)


def apply() -> int:
    # S6-B3040: idempotency guard BEFORE any write.
    t0 = rd(T)
    assert "SPLIT_PAIRS" not in rd(S), (
        "already applied - refusing before any file is written")
    assert "def test_b2931_split_is_an_exact_partition" in t0, (
        "b2931 has NOT landed: re-deriving against registrations that do not "
        "exist would leave GATES naming absent strategies (S6-B2931)")

    N = nl(S)

    # ---- 1. the pair map and the extended GATES ------------------------
    sub(S,
        "GATES = {" + N +
        "    \"smc_equal_highs_sweep_short\": (\"smc_equal_highs_swept\", \"smc_bos_bearish\")," + N +
        "    \"turtle_soup_short\": (\"smc_liquidity_swept_up\", \"smc_bos_bearish\")," + N +
        "}",
        "GATES = {" + N +
        "    \"smc_equal_highs_sweep_short\": (\"smc_equal_highs_swept\", \"smc_bos_bearish\")," + N +
        "    \"turtle_soup_short\": (\"smc_liquidity_swept_up\", \"smc_bos_bearish\")," + N +
        "    # S6-B3037 (owner ruled RE-DERIVE 2026-09-23): the B2931 split" + N +
        "    # gave the B1202 arm its own registration. Each carries its" + N +
        "    # PARENT's signal pair so the same classifier runs on both." + N +
        "    \"smc_equal_highs_bos_short\": (\"smc_equal_highs_swept\", \"smc_bos_bearish\")," + N +
        "    \"turtle_soup_bos_short\": (\"smc_liquidity_swept_up\", \"smc_bos_bearish\")," + N +
        "}" + N +
        N +
        "# S6-B3037: the PAIR is the unit of analysis after the split - the" + N +
        "# question 'how much of this name rests on the added arm' is answered" + N +
        "# by the two populations, not by one name's internal split." + N +
        "SPLIT_PAIRS = {" + N +
        "    \"turtle_soup_short\": \"turtle_soup_bos_short\"," + N +
        "    \"smc_equal_highs_sweep_short\": \"smc_equal_highs_bos_short\"," + N +
        "}")

    # ---- 2. the regime disclosure on every emitted row -----------------
    # the NO_ROWS early-return appends BEFORE any regime is computed, so
    # without this those rows emit regime=None and the docstring's "every
    # emitted row" would be false - MEASURED in the worktree, 2 of 4 rows.
    sub(S,
        "            out_rows.append({\"strategy\": strat, \"verdict\": \"NO_ROWS\"," + N +
        "                             \"landed\": 0})",
        "            out_rows.append({\"strategy\": strat, \"verdict\": \"NO_ROWS\"," + N +
        "                             \"landed\": 0," + N +
        "                             \"regime\": \"NO_READABLE_ROWS\"," + N +
        "                             \"regime_note\": (" + N +
        "                                 \"no rows for this registration in this \"" + N +
        "                                 \"cube - expected on a PRE-split cube for \"" + N +
        "                                 \"the two B2931 registrations\")," + N +
        "                             \"split_pair\": SPLIT_PAIRS.get(strat)})")

    sub(S,
        "        readable = both + thesis_only + added_only + neither",
        "        readable = both + thesis_only + added_only + neither" + N +
        "        # S6-B3037: a share that CANNOT be wrong is not evidence." + N +
        "        # After the split each registration's classification is fixed" + N +
        "        # by its own gate - the parent cannot fire without the thesis" + N +
        "        # signal, the bos arm cannot fire with it - so the share is" + N +
        "        # STRUCTURAL, not measured. Say which regime produced it." + N +
        "        if not readable:" + N +
        "            regime = \"NO_READABLE_ROWS\"" + N +
        "        elif added_only == 0 and (both + thesis_only) == readable:" + N +
        "            regime = \"POST_SPLIT_STRUCTURAL_THESIS_SIDE\"" + N +
        "        elif added_only == readable:" + N +
        "            regime = \"POST_SPLIT_STRUCTURAL_BOS_SIDE\"" + N +
        "        else:" + N +
        "            regime = \"PRE_SPLIT_INFORMATIVE\"")
    sub(S,
        "            \"added_arm_only_share\": None if share is None else round(share, 4),",
        "            \"added_arm_only_share\": None if share is None else round(share, 4)," + N +
        "            \"regime\": regime," + N +
        "            \"regime_note\": (" + N +
        "                \"share is structural, fixed by this registration's own \"" + N +
        "                \"gate, not measured from the data\"" + N +
        "                if regime.startswith(\"POST_SPLIT\") else" + N +
        "                \"share is measured: both arms could have fired\")," + N +
        "            \"split_pair\": SPLIT_PAIRS.get(strat),")
    ast.parse(rd(S))
    print("  or_arm_attribution re-pointed - AST OK")

    # ---- 3. the pin, re-derived rather than retired --------------------
    TN = nl(T)
    sub(T,
        "    src = (root / \"backtest\" / \"signals\" / \"screener.py\").read_text(" + TN +
        "        encoding=\"utf-8\", errors=\"replace\")" + TN +
        "    for strat, (thesis, added) in oaa.GATES.items():" + TN +
        "        i = src.index(\"def strat_%s(\" % strat)" + TN +
        "        body = src[i:i + 1400]" + TN +
        "        assert thesis in body, (strat, thesis, \"thesis arm not in the gate\")" + TN +
        "        assert added in body, (strat, added, \"added arm not in the gate\")" + TN +
        "        # it must still be an OR of the two, not an AND - the whole question" + TN +
        "        assert \" or \" in body, (strat, \"the OR gate is gone\")",
        "    src = (root / \"backtest\" / \"signals\" / \"screener.py\").read_text(" + TN +
        "        encoding=\"utf-8\", errors=\"replace\")" + TN +
        TN +
        "    # S6-B3037 (owner ruled RE-DERIVE 2026-09-23): the B2931 split" + TN +
        "    # replaced the OR with an exact partition, so asserting the OR is" + TN +
        "    # still present would pin a roster that no longer exists. The pin" + TN +
        "    # is RE-DERIVED, not retired - it still couples GATES to the live" + TN +
        "    # screener, now by asserting the PARTITION and the PAIRING." + TN +
        "    #" + TN +
        "    # The anchors are the EXECUTABLE form s.get(\"<signal>\" and not the" + TN +
        "    # bare signal name: b2931 writes 'the B1202 smc_bos_bearish OR-arm" + TN +
        "    # now lives in ...' into the PARENT's comment, so a bare" + TN +
        "    # `added not in body` check would match prose and test nothing" + TN +
        "    # (L748 - anchor on something that cannot appear in prose)." + TN +
        "    # The body must stop at the NEXT def. The pre-split pin sliced a" + TN +
        "    # fixed 1400 chars, which was safe only while nothing sat between" + TN +
        "    # the two gates - b2931 inserts each bos registration IMMEDIATELY" + TN +
        "    # after its parent, so a fixed window spills into the sibling and" + TN +
        "    # finds the added arm there. MEASURED: this exact assertion failed" + TN +
        "    # that way in the worktree before the bound was added." + TN +
        "    def _gate_body(name):" + TN +
        "        k = src.index(\"def strat_%s(\" % name)" + TN +
        "        e = src.find(\"\\ndef \", k + 1)" + TN +
        "        return src[k:e if e != -1 else len(src)]" + TN +
        TN +
        "    for parent, bos in oaa.SPLIT_PAIRS.items():" + TN +
        "        thesis, added = oaa.GATES[parent]" + TN +
        "        assert oaa.GATES[bos] == (thesis, added), (" + TN +
        "            bos, \"the bos registration must carry its parent's pair\")" + TN +
        TN +
        "        pbody = _gate_body(parent)" + TN +
        "        assert ('s.get(\"%s\"' % thesis) in pbody, (" + TN +
        "            parent, thesis, \"the thesis arm left the parent\")" + TN +
        "        assert ('s.get(\"%s\"' % added) not in pbody, (" + TN +
        "            parent, added," + TN +
        "            \"the B1202 arm is STILL executable in the parent - the \"" + TN +
        "            \"split did not land, so the recorded shares would again \"" + TN +
        "            \"describe two populations under one name\")" + TN +
        TN +
        "        bbody = _gate_body(bos)" + TN +
        "        assert ('s.get(\"%s\"' % added) in bbody, (" + TN +
        "            bos, added, \"the added arm is not in the bos gate\")" + TN +
        "        assert ('not s.get(\"%s\"' % thesis) in bbody, (" + TN +
        "            bos, thesis," + TN +
        "            \"the bos gate does not EXCLUDE the thesis signal - without \"" + TN +
        "            \"that negation the two registrations overlap and the \"" + TN +
        "            \"partition is not exact, which is the property the whole \"" + TN +
        "            \"attribution now rests on\")")
    ast.parse(rd(T))
    print("  test_b1248 re-derived against the post-split code - AST OK")
    print("S6-B3037 OPTION B APPLIED - re-run or_arm_attribution on the "
          "PRE-split cube and confirm the parents' rows are unchanged and "
          "now read regime PRE_SPLIT_INFORMATIVE, then run the pyramid gate")
    return 0


if __name__ == "__main__":
    sys.exit(apply())
