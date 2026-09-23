#!/usr/bin/env python
"""HELD PATCH - S6-B3037 OPTION A (retire the B1248 OR-arm attribution).

Source: this file. Derived from S6-B3043 (the landed-trade measurement) and
S6-B3046 (the retraction of my coupling-check objection); it reads
EXECUTION_QUEUE.md and backtest/tests/test_unit.py and stores nothing.

*** NOT APPLIED. REQUIRES THE OWNER'S RULING ON S6-B3037 FIRST. ***
*** AND IT APPLIES ONLY AFTER b2931_split_patch.py HAS LANDED.   ***

WHY THIS IS WRITTEN BEFORE THE RULING. The owner's own sequencing rule for
this repo is IMPLEMENT DOES NOT MEAN MERGE (S6-B2984): a change may be
written and validated while it is held unapplied, because writing it takes
no decision and holding it takes no risk. Preparing the patch means the
ruling costs one command instead of a batch. It does NOT pre-empt the
ruling: nothing here runs until the owner says retire.

WHAT OPTION A DOES, AND WHY THE OBJECTIONS TO IT RETIRED.
  test_b1248_or_arm_attribution_separates_the_added_arm asserts that each of
  two SHORT strategies still contains an " or " in its source, because
  scripts/or_arm_attribution.py recorded per-arm shares and those shares
  only describe the code while the OR stands. The owner-ruled S6-B2931 split
  replaces that OR with an exact partition, so the pin fires BY DESIGN and
  the recorded shares describe a roster that will not exist.

  Objection 1 - the partition was argued from gate text, never measured on
  landed trades. RETIRED at S6-B3043: running scripts/or_arm_attribution.py
  on cube output_r5_merged_1_7 gives smc_equal_highs_sweep_short 838 landed
  with 838 readable splitting 2 both / 304 thesis-only / 532 added-only / 0
  neither, and turtle_soup_short 1880 landed with 1880 readable splitting
  58 / 253 / 1569 / 0. Both sum exactly with nothing unattributable.

  Objection 2 - retiring the script retires the measurement. RETIRED: the
  numbers are persisted at
  output_audit/output_r5_merged_1_7_or_arm_attribution.json, which this
  patch does NOT delete. Retiring the producer does not retire the record.

  Objection 3 - the pin is the only check coupling or_arm_attribution.GATES
  to the live screener. RETRACTED BY ME at S6-B3046 after reading
  b2931_split_patch.py lines 259-306 in full: the split ships
  test_b2931_split_is_an_exact_partition, which imports the four live
  screener functions and makes 16 behavioural assertions across four bar
  shapes. That is a STRONGER coupling check than a substring test on source
  text - re-merge the OR and its sweep-only assertion fails.

THE ASYMMETRY, STATED SO THE OWNER CAN DISCOUNT IT. Only option A is
prepared. Option B (re-derive the shares against the two new registrations)
cannot be prepared yet, because its GATES must name registrations that do
not exist until b2931 applies. So the existence of this file is evidence
about what is PREPARABLE, not about which option is better.

APPLY CHECKLIST (after an owner ruling of "retire", and after b2931):

    python output_audit/held_patches/b3037a_retire_or_arm_attribution.py
    python -m pytest backtest/tests/test_unit.py -q -k "b1248 or b2931"
    #   #315: names the pin this change REMOVES (b1248) and the pin that
    #   inherits its job (b2931's partition check). Both must be named,
    #   because the whole argument for retiring is that b2931 covers it.
    python scripts/pyramid_gate.py --out output_audit/b3037a_apply_gate.json \\
        -- backtest/tests/test_unit.py backtest/tests/test_integration.py -q
"""
import ast
import io
import sys

T = "backtest/tests/test_unit.py"
SCRIPT = "scripts/or_arm_attribution.py"
ARTIFACT = "output_audit/output_r5_merged_1_7_or_arm_attribution.json"


def rd(p):
    return io.open(p, encoding="utf-8", newline="").read()


def nl(p):
    text = rd(p)
    return "\r\n" if text.count("\r\n") * 2 > text.count("\n") else "\n"


def apply() -> int:
    # S6-B3040: the idempotency guard runs BEFORE any write.
    src = rd(T)
    assert "def test_b1248_or_arm_attribution_separates_the_added_arm" in src, (
        "already applied, or the pin was renamed - refusing before any write")

    # The split must have landed, or retiring the pin removes the ONLY
    # coupling check rather than the redundant one. This is the whole
    # argument for option A, so it is asserted rather than assumed.
    assert "def test_b2931_split_is_an_exact_partition" in src, (
        "b2931 has NOT been applied: test_b2931_split_is_an_exact_partition "
        "is absent, so retiring b1248 now would leave the split uncoupled to "
        "the live screener. Apply b2931 first (S6-B2931).")

    from pathlib import Path as _P
    assert _P(ARTIFACT).exists(), (
        "the persisted measurement %s is missing - retiring the producer is "
        "only safe while the record it produced survives (S6-B3043)"
        % ARTIFACT)

    N = nl(T)
    i = src.index("def test_b1248_or_arm_attribution_separates_the_added_arm")
    # the function ends at the next top-level def
    j = src.index((N + N + "def "), i)
    removed = src[i:j].count(N) + 1
    io.open(T, "w", encoding="utf-8", newline="").write(src[:i] + src[j + 2 * len(N):])
    ast.parse(rd(T))
    print("  removed test_b1248 (%d lines) - AST OK" % removed)

    print("S6-B3037 OPTION A APPLIED. The producer script is left on disk on "
          "purpose: retiring the PIN stops the false failure, and deleting "
          "the script is a separate call the owner has not made. The measured "
          "shares remain at %s." % ARTIFACT)
    return 0


if __name__ == "__main__":
    print(__doc__.split("APPLY CHECKLIST")[0])
    print("REFUSING TO RUN: this patch requires an explicit owner ruling on "
          "S6-B3037 (retire). Re-run with --i-have-the-owner-ruling once it "
          "is given.")
    if "--i-have-the-owner-ruling" not in sys.argv:
        sys.exit(3)
    sys.exit(apply())
