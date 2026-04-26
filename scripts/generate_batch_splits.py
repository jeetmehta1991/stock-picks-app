"""
scripts/generate_batch_splits.py
Generate 5 ticker batch splits for parallel Phase 1B runs.

Usage:
    python scripts/generate_batch_splits.py

Outputs:
    scripts/batch_splits.json  — 5 lists of tickers
    Prints exact run commands for each batch
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest.data.universe import get_sp500_constituents, ETFS_FULL

# Full universe — same order as Phase 1B
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

print(f"Universe: {n} tickers → 5 batches")
for i, batch in enumerate(batches):
    print(f"\nBatch {i+1}: {len(batch)} tickers ({batch[0]} → {batch[-1]})")

print("\n" + "="*70)
print("FULL RUN COMMANDS (run each in a separate terminal):")
print("="*70)
phase = "1b"
for i, batch in enumerate(batches):
    tickers = ",".join(batch)
    print(f"\n# Terminal {i+1} — Batch {i+1} ({len(batch)} tickers)")
    print(f'nohup python backtest/run_phase1a.py --phase {phase} \\')
    print(f'  --tickers {tickers} \\')
    print(f'  --output-dir output_1b_batch{i+1} \\')
    print(f'  --no-git \\')
    print(f'  > batch{i+1}.log 2>&1 &')
    print(f'echo "Batch {i+1} PID: $!"')

print("\n" + "="*70)
print("TEST COMMANDS (1 ticker per batch, 2022-01-01 to 2022-01-31):")
print("="*70)
test_tickers = [batches[i][0] for i in range(5)]
for i, ticker in enumerate(test_tickers):
    print(f"\n# Terminal {i+1} — Batch {i+1} test ({ticker})")
    print(f'nohup python backtest/run_phase1a.py --phase {phase} \\')
    print(f'  --tickers {ticker} \\')
    print(f'  --start 2022-01-01 --end 2022-01-31 \\')
    print(f'  --output-dir output_1b_batch{i+1}_test \\')
    print(f'  --no-git \\')
    print(f'  > batch{i+1}_test.log 2>&1 &')
    print(f'echo "Batch {i+1} test PID: $!"')
