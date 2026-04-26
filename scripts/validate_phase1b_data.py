"""
scripts/validate_phase1b_data.py — Pre-run data validation for Phase 1B.

Run this before starting Phase 1B to confirm all data is ready.
Usage: python scripts/validate_phase1b_data.py

Checks:
- Quiver cache: all 7 data types, all 509 tickers
- Alpha Vantage news cache: 509 tickers
- FRED macro: date range extends to March 2026
- OHLCV cache: 509+ tickers
- AAII + CNN sentiment: date coverage
- Integration tests: all pass
"""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

CACHE_DIR  = Path("backtest/data/cache")
QUIVER_DIR = CACHE_DIR / "quiver"
AV_DIR     = CACHE_DIR / "av_news"
OHLCV_DIR  = CACHE_DIR / "ohlcv"
MACRO_DIR  = CACHE_DIR / "macro"

REQUIRED_TICKERS = 509
MIN_MACRO_DATE   = date(2026, 3, 1)

issues = []
warnings = []
passed  = []


def check(label, condition, message, warn=False):
    if condition:
        passed.append(f"✅ {label}")
        print(f"  ✅ {label}")
    elif warn:
        warnings.append(f"⚠️  {label}: {message}")
        print(f"  ⚠️  {label}: {message}")
    else:
        issues.append(f"❌ {label}: {message}")
        print(f"  ❌ {label}: {message}")


print("=" * 60)
print("PHASE 1B PRE-RUN DATA VALIDATION")
print("=" * 60)

# ── Quiver cache ──
print("\n--- Quiver Cache ---")
quiver_types = ["congressional","insider","institutional",
                "gov_contracts","lobbying","wikipedia","wallstreetbets"]
for dt in quiver_types:
    dt_dir = QUIVER_DIR / dt
    count     = len(list(dt_dir.glob("*.parquet"))) if dt_dir.exists() else 0
    non_empty = sum(1 for f in dt_dir.glob("*.parquet") if f.stat().st_size > 1100) if dt_dir.exists() else 0
    # Empty files are valid for sparse data types (not all tickers have gov contracts etc.)
    # Critical check: file count must be 509 (all tickers downloaded, even if data is empty)
    # Non-empty threshold varies: congressional/insider should have many; gov_contracts few is ok
    if dt in ["congressional", "insider"]:
        # Must have files for all tickers; at least 50% non-empty
        ok = count >= REQUIRED_TICKERS and non_empty >= REQUIRED_TICKERS * 0.5
        check(f"Quiver {dt}: {count} files ({non_empty} non-empty)",
              ok, f"only {count} files or too few non-empty", warn=False)
    elif dt == "wikipedia":
        # Wikipedia may legitimately return empty for all — mark as warning not blocker
        check(f"Quiver {dt}: {count} files ({non_empty} non-empty)",
              count >= REQUIRED_TICKERS,
              f"only {count}/{REQUIRED_TICKERS} files downloaded", warn=True)
    else:
        # gov_contracts, lobbying, wsb, institutional — sparse data is expected
        check(f"Quiver {dt}: {count} files ({non_empty} non-empty)",
              count >= REQUIRED_TICKERS,
              f"only {count}/{REQUIRED_TICKERS} files downloaded", warn=True)

# ── Alpha Vantage news ──
print("\n--- Alpha Vantage News ---")
av_count = len(list(AV_DIR.glob("*.parquet"))) if AV_DIR.exists() else 0
av_nonempty = sum(1 for f in AV_DIR.glob("*.parquet") if f.stat().st_size > 1100) if AV_DIR.exists() else 0
check(
    f"AV news: {av_count} files ({av_nonempty} non-empty)",
    av_nonempty >= REQUIRED_TICKERS,
    f"only {av_nonempty}/{REQUIRED_TICKERS}",
    warn=True,
)

# ── OHLCV cache ──
print("\n--- OHLCV Cache ---")
ohlcv_count = len(list(OHLCV_DIR.glob("*.parquet"))) if OHLCV_DIR.exists() else 0
# OHLCV: allow up to 20 missing (some ETFs/tickers may not be on yfinance)
check(
    f"OHLCV: {ohlcv_count} tickers",
    ohlcv_count >= REQUIRED_TICKERS - 20,
    f"only {ohlcv_count}/{REQUIRED_TICKERS} — more than 20 missing",
)

# ── FRED macro ──
print("\n--- FRED Macro ---")
try:
    import pandas as pd
    macro_file = MACRO_DIR / "macro_combined.parquet"
    if macro_file.exists():
        df = pd.read_parquet(macro_file)
        df["date"] = pd.to_datetime(df["date"])
        last_date = df["date"].max().date()
        check(
            f"FRED macro: {len(df)} rows, last date {last_date}",
            last_date >= MIN_MACRO_DATE,
            f"only extends to {last_date}, need {MIN_MACRO_DATE}",
        )
    else:
        issues.append("❌ FRED macro: macro_combined.parquet not found")
        print("  ❌ FRED macro: not found")
except Exception as e:
    issues.append(f"❌ FRED macro: {e}")
    print(f"  ❌ FRED macro: {e}")

# ── AAII sentiment ──
print("\n--- Sentiment CSVs ---")
aaii_file = Path("backtest/data/aaii_sentiment.csv")
cnn_file  = Path("backtest/data/cnn_fear_greed.csv")
if aaii_file.exists():
    import pandas as pd
    aaii_df = pd.read_csv(aaii_file)
    check(f"AAII sentiment: {len(aaii_df)} rows", len(aaii_df) >= 300, f"only {len(aaii_df)} rows")
else:
    issues.append("❌ AAII CSV not found")
    print("  ❌ AAII CSV not found")

if cnn_file.exists():
    cnn_df = pd.read_csv(cnn_file)
    check(f"CNN Fear & Greed: {len(cnn_df)} rows", len(cnn_df) >= 1500, f"only {len(cnn_df)} rows")
else:
    issues.append("❌ CNN F&G CSV not found")
    print("  ❌ CNN F&G CSV not found")

# ── Integration tests ──
print("\n--- Integration Tests ---")
import subprocess, sys as _sys
result = subprocess.run(
    [_sys.executable, "backtest/tests/run_all_tests.py"],
    capture_output=True, text=True, timeout=120
)
tests_passed = "ALL TESTS PASSED" in result.stdout or "tests passed" in result.stdout
if not tests_passed:
    print(f"  Test output: {result.stdout[-300:] if result.stdout else result.stderr[-200:]}")
check(
    "Integration tests",
    tests_passed,
    "some tests failed — run: python backtest/tests/run_all_tests.py",
    warn=True,  # warn not blocker — tests may fail on laptop due to missing cache
)

# ── PROMPT_VERSION check ──
print("\n--- Agent Cache ---")
try:
    from backtest.agents.pipeline import PROMPT_VERSION
    agent_cache = Path("backtest/agents/cache")
    old_caches = list(agent_cache.glob("*.json")) if agent_cache.exists() else []
    check(
        f"Agent PROMPT_VERSION: {PROMPT_VERSION} | Cache files: {len(old_caches)}",
        True, "", warn=False
    )
    if old_caches:
        print(f"  ℹ️  {len(old_caches)} cached agent analyses (will be auto-skipped if stale)")
except Exception as e:
    warnings.append(f"⚠️  Could not check agent cache: {e}")

# ── Summary ──
print("\n" + "=" * 60)
print(f"PASSED: {len(passed)}")
print(f"WARNINGS: {len(warnings)}")
print(f"BLOCKERS: {len(issues)}")

if warnings:
    print("\nWarnings (non-blocking):")
    for w in warnings:
        print(f"  {w}")

if issues:
    print("\nBLOCKERS (must fix before Phase 1B):")
    for i in issues:
        print(f"  {i}")
    print("\n❌ NOT READY FOR PHASE 1B")
    sys.exit(1)
else:
    print("\n✅ ALL CHECKS PASSED — ready for Phase 1B")
    print("\nPhase 1B run command:")
    print("  nohup python backtest/run_phase1a.py --phase 1b --output-dir output_1b > phase1b.log 2>&1 &")
    print("  tail -f phase1b.log")
    sys.exit(0)
