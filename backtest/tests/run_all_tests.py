"""
Master test runner — run all tests before Phase 1B.
Usage: python backtest/tests/run_all_tests.py

All tests must pass before starting any backtest run.
"""
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def run_test_file(path: str) -> tuple[int, int, list]:
    """Run a test file, return (passed, total, failed_names)."""
    result = subprocess.run(
        [sys.executable, path],
        capture_output=True, text=True
    )
    output = result.stdout + result.stderr
    lines = output.strip().split('\n')

    passed = sum(1 for l in lines if l.startswith('✅'))
    failed = [l for l in lines if l.startswith('❌')]
    # Parse total from summary line
    for line in reversed(lines):
        if '/' in line and 'passed' in line:
            try:
                total = int(line.split('/')[1].split()[0])
                break
            except:
                total = passed + len(failed)
            break
    else:
        total = passed + len(failed)

    for line in lines:
        print(f"  {line}")
    return passed, total, failed


if __name__ == "__main__":
    print("=" * 60)
    print("MASTER TEST RUNNER — Pre-Phase 1B Validation")
    print("=" * 60)

    test_files = [
        ("Integration Tests", "backtest/tests/test_integration.py"),
        ("Unit Tests",        "backtest/tests/test_unit.py"),
        ("E2E Smoke Test",    "backtest/tests/test_e2e.py"),
    ]

    total_passed = 0
    total_all    = 0
    all_failed   = []

    for name, path in test_files:
        print(f"\n--- {name} ---")
        p, t, f = run_test_file(path)
        total_passed += p
        total_all    += t
        all_failed.extend(f)

    print("\n" + "=" * 60)
    print(f"TOTAL: {total_passed}/{total_all} tests passed")
    if all_failed:
        print(f"FAILED TESTS:")
        for f in all_failed:
            print(f"  {f}")
        print("\n❌ DO NOT RUN PHASE 1B — fix failing tests first")
        sys.exit(1)
    else:
        print("✅ ALL TESTS PASSED — safe to proceed")
        sys.exit(0)
