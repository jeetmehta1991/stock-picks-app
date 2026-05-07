"""
scripts/generate_batch_splits.py
Generate 5 ticker batch splits for parallel Phase 1B runs.

Usage:
    python scripts/generate_batch_splits.py

Outputs:
    scripts/batch_splits.json  — 5 lists of tickers
    Prints exact test and full run commands for each batch
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest.data.universe import get_sp500_constituents, ETFS_FULL

# Full universe - same order as Phase 1B
universe = list(dict.fromkeys(get_sp500_constituents(500) + ETFS_FULL))
n = len(universe)
batch_size = n // 5
batches = []
for i in range(5):
    start = i * batch_size
    end   = start + batch_size if i < 4 else n
    batches.append(universe[start:end])

# Save splits
splits_file = Path('scripts/batch_splits.json')
splits_file.write_text(json.dumps({f"batch_{i+1}": b for i,b in enumerate(batches)}, indent=2))

# Verify no overlap, no missing
all_tickers = [t for b in batches for t in b]
assert len(all_tickers) == n, f"Count mismatch: {len(all_tickers)} vs {n}"
assert len(set(all_tickers)) == n, "Overlap detected"
print(f"[OK] Universe: {n} tickers -> 5 batches (no overlap, no missing)\n")
for i, batch in enumerate(batches):
    print(f"  Batch {i+1}: {len(batch)} tickers ({batch[0]} -> {batch[-1]})")

# Representative test tickers - one per major sector from each batch
# These are tickers known to have signal activity in Jan 2022
TEST_TICKERS = {
    1: "AAPL",   # Batch 1 - Information Technology (large, active signals)
    2: "CVS",    # Batch 2 - Health Care
    3: "JPM",    # Batch 3 - Financials (high volume, many signals)
    4: "NVDA",   # Batch 4 - Semiconductors (volatile, good for testing exits)
    5: "XLE",    # Batch 5 - Energy ETF (sector-level signals)
}
# Verify test tickers are actually in their respective batches
for i, ticker in TEST_TICKERS.items():
    assert ticker in batches[i-1], f"{ticker} not in batch {i}"

print("\n" + "="*70)
print("BEFORE RUNNING: Pre-populate index.json (prevents race condition)")
print("="*70)
print("python scripts/prepopulate_cache_index.py")

print("\n" + "="*70)
print("STEP 1 - TEST (1 ticker per batch, Jan 2022, ~5 min each):")
print("Run all 5 simultaneously in separate Git Bash terminals")
print("="*70)
phase = "1b"
for i, ticker in TEST_TICKERS.items():
    print(f"\n# Terminal {i} - Batch {i} test ({ticker})")
    print(f"nohup python backtest/run_phase1a.py --phase {phase} \\")
    print(f"  --tickers {ticker} \\")
    print(f"  --start 2022-01-01 --end 2022-01-31 \\")
    print(f"  --output-dir output_1b_batch{i}_test \\")
    print(f"  --no-git \\")
    print(f"  > batch{i}_test.log 2>&1 &")
    print(f'echo "Batch {i} test PID: $!"')

print("\n# After all 5 tests complete - validate and merge:")
test_dirs = " ".join([f"output_1b_batch{i}_test" for i in range(1,6)])
print(f"python scripts/merge_batch_outputs.py \\")
print(f"  --input-dirs {test_dirs} \\")
print(f"  --output-dir output_1b_test_merged")

print("\n" + "="*70)
print("STEP 2 - FULL RUN (after test passes and owner approves):")
print("Run all 5 simultaneously - ~12-15 hours total")
print("="*70)
for i, batch in enumerate(batches):
    tickers = ",".join(batch)
    print(f"\n# Terminal {i+1} - Batch {i+1} ({len(batch)} tickers)")
    print(f"nohup python backtest/run_phase1a.py --phase {phase} \\")
    print(f"  --tickers {tickers} \\")
    print(f"  --output-dir output_1b_batch{i+1} \\")
    print(f"  --no-git \\")
    print(f"  > batch{i+1}.log 2>&1 &")
    print(f'echo "Batch {i+1} PID: $!"')

print("\n" + "="*70)
print("AFTER ALL BATCHES COMPLETE - commit sequence:")
print("="*70)
print("""
1. git status                        # verify clean before anything
2. git add backtest/agents/cache/    # agent cache (shared across batches)
3. git add output_1b_batch1/ output_1b_batch2/ output_1b_batch3/ output_1b_batch4/ output_1b_batch5/
4. git commit -m "Phase 1B: all 5 batches complete"
5. git pull --rebase origin main
6. git push origin main
7. git log -1 origin/main            # verify push landed
8. python scripts/merge_batch_outputs.py --input-dirs output_1b_batch1 output_1b_batch2 output_1b_batch3 output_1b_batch4 output_1b_batch5 --output-dir output_1b_final
9. git add output_1b_final/
10. git commit -m "Phase 1B: merged final results"
11. git pull --rebase origin main && git push origin main
""")
