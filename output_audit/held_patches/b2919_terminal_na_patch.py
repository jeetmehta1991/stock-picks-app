#!/usr/bin/env python
"""HELD PATCH - S6-B2919 (owner ruled 2026-09-22: terminal N/A).

APPLY AT CHAIN DONE ONLY. scripts/run_postconfig.py is the battery
supervisor loaded fresh at every landing (S6-B2957 / L836 addendum), so
applying this while the b2944b chain runs would grade earlier and later
configs under different disposition rules. The chain-done checklist runs:

    python output_audit/held_patches/b2919_terminal_na_patch.py
    python -m pytest backtest/tests/test_unit.py -q -k "b2919_below_power or b2612"
    #   S6-B3031: the token was b2919_terminal and it collects ZERO
    #   tests - the pin is named test_b2919_below_power_is_terminal_na
    #   and -k does SUBSTRING matching, so b2919_terminal is not in it.
    #   This selector never ran the patch's own pin, which is why the
    #   KeyError below went undiscovered until a full-suite diff.
    #   S6-B3030 (#315): b2612 is NOT decoration. This patch adds an N/A
    #   branch to the very fail-closed path
    #   test_b2612_step2_cube_without_gate_verdicts_fails_closed pins, so
    #   that pin MUST move with the ruling or the two contradict. The old
    #   selector named only the pin this patch ADDS, so the conflict
    #   surfaced at the pyramid late in the apply batch instead of here.
    python scripts/pyramid_gate.py --out output_audit/b2919_apply_gate.json \
        -- backtest/tests/test_unit.py backtest/tests/test_integration.py -q

WHAT IT CHANGES, and why the shape is what it is:
  * run_postconfig.py's step2_grade_auto caller (the B2612 block) gains an
    N/A branch: when grid_step2_graded says "not graded" AND the grid's own
    step2 block carries an HONEST not-evaluable verdict - BELOW_POWER_FLOOR,
    NO_HOLDOUT_ROWS or NO_EXIT_SELECTABLE - the step is recorded N/A
    carrying that verdict and its reason, and the battery does not fail.
    "Not enough data" is an evidenced answer (the owner's ruling), not a
    failure needing hand disposition.
  * The L642 fail-closed path is PRESERVED for the malformed case: a
    declared Step-2 cube whose grid carries NO step2 block, or a step2
    block with no such verdict, still FAILS closed - that is a grader
    defect, not an honest answer.
  * grid_step2_graded itself is untouched: it answers "did the grader
    grade?" truthfully, and the DISPOSITION of an honest no is the
    caller's question (L845: the honest producer and the closing consumer
    are different files, and this ruling lands in the consumer).

VALIDATED IN AN ISOLATED WORKTREE before being parked here - see the
b2919/b2931 validation note in the queue row that shipped this file; the
live tree is untouched until CHAIN DONE.
"""
import ast
import io
import sys

def rd(p):
    return io.open(p, encoding="utf-8", newline="").read()

def nl(p):
    # S6-B3026: the DOMINANT ending, not ANY occurrence. This helper runs
    # at CHAIN DONE against files edited across the whole session, and the
    # presence form lets ONE foreign line convert every replacement the
    # patch writes - the amplification L850 records, which turned a single
    # landing row into a 120-line diff preflight C13 refused at B3023. A
    # majority test is unmoved by a stray line and identical otherwise.
    text = rd(p)
    return "\r\n" if text.count("\r\n") * 2 > text.count("\n") else "\n"

def sub(path, old, new, count=1):
    s = rd(path)
    n = s.count(old)
    assert n == count, "anchor in %s occurs %d (want %d): %r" % (
        path, n, count, old[:70])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new))
    print("  patched", path)

V = "scripts/run_postconfig.py"


def apply() -> int:
    N = nl(V)

    # 1. a sentinel initialised beside ok2/why2, same scope as the append
    sub(V,
        "    ok2 = g.returncode == 0 and grid_out.exists()" + N +
        "    why2 = \"\"",
        "    ok2 = g.returncode == 0 and grid_out.exists()" + N +
        "    why2 = \"\"" + N +
        "    step2_na_row = None   # S6-B2919: set on an honest not-evaluable verdict")

    # 2. the N/A branch inside the B2612 block, and the append made
    #    sentinel-aware
    sub(V,
        "        if not why2:" + N +
        "            graded, why2 = grid_step2_graded(_grid)" + N +
        "            ok2 = bool(graded)" + N +
        "            why2 = (\"Step-2 gate verdict present: \" if graded else" + N +
        "                    \"Step-2 cube with NO gate verdict (fail closed, L642): \") + why2" + N +
        "    results.append((\"step2_grade_auto\", \"PASS\" if ok2 else \"FAIL\",",
        "        if not why2:" + N +
        "            graded, why2 = grid_step2_graded(_grid)" + N +
        "            ok2 = bool(graded)" + N +
        "            why2 = (\"Step-2 gate verdict present: \" if graded else" + N +
        "                    \"Step-2 cube with NO gate verdict (fail closed, L642): \") + why2" + N +
        "            if not graded:" + N +
        "                # S6-B2919 (owner ruled 2026-09-22): an HONEST" + N +
        "                # not-evaluable verdict is a terminal N/A carrying" + N +
        "                # its reason - an evidenced answer, not a failure" + N +
        "                # needing hand disposition. The fail-closed path" + N +
        "                # remains for a grid whose step2 block is ABSENT or" + N +
        "                # carries no such verdict (the L642 malformed case)." + N +
        "                _s2b = _grid.get(\"step2\")" + N +
        "                _hv = (_s2b.get(\"verdict\")" + N +
        "                       if isinstance(_s2b, dict) else None)" + N +
        "                if _hv in (\"BELOW_POWER_FLOOR\", \"NO_HOLDOUT_ROWS\"," + N +
        "                           \"NO_EXIT_SELECTABLE\"):" + N +
        "                    step2_na_row = (" + N +
        "                        \"step2_grade_auto\", \"N/A\"," + N +
        "                        \"%s: %s - terminal N/A per owner ruling \"" + N +
        "                        \"2026-09-22 (S6-B2919)\"" + N +
        "                        % (_hv, str(_s2b.get(\"reason\") or \"\")[:160]))" + N +
        "    if step2_na_row is not None:" + N +
        "        results.append(step2_na_row)" + N +
        "    else:" + N +
        "        results.append((\"step2_grade_auto\", \"PASS\" if ok2 else \"FAIL\",")

    # 3. close the else-block: the original append's continuation lines gain
    #    one indent level via the trailing-lines anchor
    sub(V,
        "                    f\"exit {g.returncode}; {label} -> {grid_out.name}\"" + N +
        "                    + (f\"; {why2[:200]}\" if why2 else \"\")" + N +
        "                    + (\"\" if ok2 or why2 else f\"; {_tail(g)[:160]}\")))",
        "                        f\"exit {g.returncode}; {label} -> {grid_out.name}\"" + N +
        "                        + (f\"; {why2[:200]}\" if why2 else \"\")" + N +
        "                        + (\"\" if ok2 or why2 else f\"; {_tail(g)[:160]}\")))")

    ast.parse(rd(V))
    print("  run_postconfig.py N/A branch applied - AST OK")

    T = "backtest/tests/test_unit.py"
    TN = nl(T)
    TEST = '''


def test_b2919_below_power_is_terminal_na(monkeypatch, tmp_path):
    """S6-B2919 (owner ruled 2026-09-22): a below-power Step-2 result is a
    terminal N/A carrying its reason - and the L642 fail-closed path stays
    for a grid whose step2 block is absent.

    Fixture mirrors the B2612 harness: _run is monkeypatched to write the
    planted grid json, so the caller's disposition logic is exercised on
    the real path with no engine involved.
    """
    import json as _json
    from pathlib import Path as _P

    import scripts.run_postconfig as rp

    def make_run(grid_doc):
        def _run(cmd, env=None):
            class R:
                returncode = 0
                stdout = b""
                stderr = b""
            outs = [str(a) for a in cmd if str(a).endswith(".json")]
            if outs:
                _P(outs[-1]).write_text(_json.dumps(grid_doc),
                                        encoding="utf-8")
            return R()
        return _run

    cube = tmp_path / "cube"
    cube.mkdir()
    (cube / "trade_exit_detail.csv").write_text("x", encoding="utf-8")
    manifest = {"window": {"start": "2024-05-05", "end": "2025-05-05"},
                "arms": [{"env": {}}]}

    honest = {"results": [{"verdict": "BELOW_POWER_FLOOR"}],
              "step2": {"verdict": "BELOW_POWER_FLOOR",
                        "reason": "holdout n 7 < min_n 10 on 'ts10'"}}
    malformed = {"results": [{"verdict": "RANKED"}]}

    # S6-B3032: the family's OWN key set, not an empty dict.
    # run_family builds its label as p[k] for every key the family
    # declares (run_postconfig.py:619), so {} raises KeyError on the
    # first one. institutional_committed_growth_long declares four:
    # P4 min_consecutive_quarters, P5 growth_lookback_quarters,
    # P6 growth_multiple, P9 ema_span. These values mirror the B2612
    # harness this fixture claims to mirror (test_unit.py:30813).
    _p = {"min_consecutive_quarters": 4, "growth_lookback_quarters": 4,
          "growth_multiple": 1.1, "ema_span": 200}

    # arm 1: honest verdict -> N/A, verdict and reason carried, no FAIL row
    monkeypatch.setattr(rp, "_run", make_run(honest))
    res, _, _, _ = rp.run_institutional(cube, _p, manifest, step=2)
    by = {n: (st, m) for n, st, m in res}
    assert by["step2_grade_auto"][0] == "N/A", by["step2_grade_auto"]
    assert "BELOW_POWER_FLOOR" in by["step2_grade_auto"][1]
    assert "S6-B2919" in by["step2_grade_auto"][1]
    assert "holdout n 7" in by["step2_grade_auto"][1]

    # arm 2: NO step2 block on a declared Step-2 cube -> FAIL closed (L642)
    monkeypatch.setattr(rp, "_run", make_run(malformed))
    res2, _, _, _ = rp.run_institutional(cube, _p, manifest, step=2)
    by2 = {n: (st, m) for n, st, m in res2}
    assert by2["step2_grade_auto"][0] == "FAIL", by2["step2_grade_auto"]
'''
    raw = rd(T)
    assert "test_b2919_below_power_is_terminal_na" not in raw
    io.open(T, "a", encoding="utf-8", newline="").write(
        TEST.replace("\n", TN) if TN != "\n" else TEST)
    ast.parse(rd(T))
    print("  pin appended - AST OK")
    print("S6-B2919 TERMINAL-N/A APPLIED - run the pyramid gate before committing")
    return 0


if __name__ == "__main__":
    sys.exit(apply())
