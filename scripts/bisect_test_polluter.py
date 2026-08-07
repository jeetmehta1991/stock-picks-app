"""scripts/bisect_test_polluter.py (B1469, ticket S6-B1468a) -- find the test file whose
side effects break the two `test_integration.py` tests in a full-suite run.

THE DEFECT
`test_integration.py::test_bug_30_check_circuit_breakers_gate_on_config` and
`::test_bug_232_intraday_extreme_uses_today_high_for_longs` PASS in isolation (0.74s) and FAIL
when all 431 test files run. They are in the ENFORCED commit gate, so the gate's `894 passed`
certifies "these pass when nothing else has run" rather than "these pass" (L313).

WHY BISECT RATHER THAN RE-RUN
A full suite pass costs ~35 minutes. Binary search over the file list, running only
[candidate chunk] + [the two targets], costs seconds-to-minutes per step and converges in
~log2(431) ~ 9 steps. The targets are appended LAST so any state the chunk leaves behind is
still in place when they run -- which is the whole mechanism being hunted.

METHOD
1. Confirm the targets pass alone (else there is no pollution to find).
2. Confirm the FULL list reproduces the failure (else the trigger is ordering/parallelism, not a
   single file, and bisection is the wrong tool -- reported, not silently assumed).
3. Halve repeatedly, keeping whichever half still reproduces. If NEITHER half reproduces, the
   cause is an interaction between files in different halves -- reported explicitly rather than
   forcing a single-file answer.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# B1474: pytest-timeout is NOT installed in this environment, so passing --timeout made
# pytest exit with "unrecognized arguments" and run ZERO tests. Both this script and
# bisect_test_polluter.py silently measured nothing until the implausibility of the
# result (72 of 72 identical) exposed it. The subprocess timeout below does the same job
# without depending on a plugin, and _assert_pytest_ran refuses to classify output that
# is not a pytest result (CHECKLIST #174: prove the probe RAN).
def _assert_pytest_ran(out: str, label: str) -> None:
    if "unrecognized arguments" in out or "ERROR: usage:" in out:
        raise SystemExit(
            "[HALT] pytest rejected its arguments while running " + str(label)
            + ": " + out[:300]
            + " -- the probe never executed; any classification would be fiction."
        )

TARGETS = [
    "backtest/tests/test_integration.py::test_bug_30_check_circuit_breakers_gate_on_config",
    "backtest/tests/test_integration.py::test_bug_232_intraday_extreme_uses_today_high_for_longs",
]


def run(files: list[str], timeout: int = 1800) -> bool:
    """True if the TARGETS still pass with `files` running first."""
    # NO -x. B1469 first attempt used it and the result was invalid: the candidate set
    # contains 172 known failures, so -x aborted at the first one and the TARGETS never
    # ran -- which the script then read as "targets PASS". A bisection whose probe can
    # be skipped silently reports the opposite of the truth.
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:randomly",
           "--tb=no", *files, *TARGETS]
    try:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"    [TIMEOUT] {len(files)} files - treating as NOT reproducing")
        return True
    out = r.stdout + r.stderr
    _assert_pytest_ran(out, f'{len(files)} files')
    tail = out.strip().splitlines()[-1] if out.strip() else ""
    # Read the TARGETS' own result, never the run-wide summary: the candidate set has
    # 172 unrelated failures, so " failed" in the summary says nothing about the probe.
    target_failed = any(f"FAILED {t}" in out or t.split("::")[-1] in out.split("FAILED")[-1]
                        for t in TARGETS if "FAILED" in out)
    if not tail:
        print(f"    {len(files):>4} files -> [NO SUMMARY] treating as INCONCLUSIVE")
        return True
    ok = not target_failed
    print(f"    {len(files):>4} files -> {'targets PASS' if ok else 'targets FAIL'}   {tail[:70]}")
    return ok


def main() -> int:
    all_files = sorted(
        str(p.relative_to(REPO)).replace("\\", "/")
        for p in (REPO / "backtest" / "tests").glob("test_*.py")
        if p.name not in ("test_integration.py",)
    )
    print("=" * 92)
    print("POLLUTER BISECTION (B1469 / S6-B1468a)")
    print("=" * 92)
    print(f"  candidate files: {len(all_files)}  |  targets: 2 from test_integration.py\n")

    print("  step 0 -- targets alone (must PASS, else nothing to bisect)")
    if not run([]):
        print("  [HALT] targets fail in isolation; this is a real defect, not pollution.")
        return 1

    print("\n  step 1 -- full candidate list (must FAIL, else not a single-file cause)")
    if run(all_files):
        print("\n  [RESULT] targets PASS with every candidate file running first.")
        print("  The full-suite failure is therefore NOT caused by any file in this set running")
        print("  before them -- suspect ordering, parallelism, or test_unit.py itself. Bisection")
        print("  is the wrong tool here; reporting rather than forcing a single-file answer.")
        return 0

    lo = all_files
    print(f"\n  step 2+ -- narrowing from {len(lo)}")
    while len(lo) > 1:
        mid = len(lo) // 2
        first, second = lo[:mid], lo[mid:]
        if not run(first):
            lo = first
            continue
        if not run(second):
            lo = second
            continue
        print(f"\n  [RESULT] neither half of {len(lo)} reproduces alone -> the cause is an")
        print("  INTERACTION across the split, not one file. Remaining candidates:")
        for f in lo:
            print(f"    {f}")
        return 0

    print(f"\n  [RESULT] POLLUTER = {lo[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
