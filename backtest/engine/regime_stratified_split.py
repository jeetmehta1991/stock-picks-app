"""DEC-153 - Regime-stratified train/test split (Pass 53 build per DEC-594 same-commit).

Joint with DEC-109 walk-forward + DEC-422 cube per-regime verdicts.

Per Pass 52 turn 119 spec: each fold's train and test sets must contain
proportional representation of each regime (calm / neutral / volatile / crisis
per DEC-542 4-class). Naive date-based folds may load one regime entirely into
train and another into test, biasing per-regime metrics.

Implementation: given a fold's date range and per-day regime labels, compute
indices that are stratified by regime. If a regime has fewer than `min_per_regime`
samples in either train or test, it is marked INSUFFICIENT_SAMPLE for that fold.

Status: PARTIAL-SPEC-ONLY → RESOLVED-DECIDED post artifact landing per DEC-594.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd

# Batch 189 (INV-051 fix) - accept BOTH vocabularies:
#   - Engine runtime taxonomy (regime_filter.py classify_regime):
#       bull / neutral / bear / crisis   (CANONICAL_FACTS F-006)
#   - DEC-542 4-class spec / DEC-153 stratifier original docstring:
#       calm / neutral / volatile / crisis
# These are orthogonal axes (trend vs volatility) that overlap only at
# 'neutral' and 'crisis'. Prior bug: REGIME_CLASSES used only the
# DEC-542 vocab, so engine outputs bull/bear silently dropped to
# 'unknown' bucket, collapsing all train/test into neutral-only.
# Fix: include the union of both vocabularies.
REGIME_CLASSES = ("bull", "neutral", "bear", "crisis", "calm", "volatile")
DEFAULT_MIN_PER_REGIME = 20  # min samples per regime per split (>=30 recommended; 20 floor)


def regime_stratified_split(
    dates: Sequence[pd.Timestamp],
    regime_labels: Sequence[str],
    train_frac: float = 0.7,
    min_per_regime: int = DEFAULT_MIN_PER_REGIME,
    seed: int = 42,
) -> Tuple[List[int], List[int], Dict[str, int]]:
    """Stratified split of (date, regime) sequence into train/test indices.

    Args:
        dates: chronologically-ordered timestamps (length N).
        regime_labels: regime per date (length N); must contain values from REGIME_CLASSES.
        train_frac: fraction of each regime's samples assigned to train (rest to test).
        min_per_regime: minimum samples required in BOTH train and test per regime.
        seed: RNG seed for reproducibility.

    Returns:
        train_idx, test_idx, regime_summary
            - train_idx, test_idx: index lists into the input arrays
            - regime_summary: {regime: train_count, regime + "_test": test_count, regime + "_status": "OK" | "INSUFFICIENT_SAMPLE"}

    Notes:
        - Within each regime, indices are sorted chronologically (preserves time-ordering
          within strata). This avoids accidentally training on future-relative-to-test
          observations within a regime.
        - Indices are NOT globally chronological - train and test interleave in time.
          This is INTENTIONAL: stratification is the goal; chronological purity is preserved
          via DEC-505 walk-forward fold boundaries (folds are time-disjoint; stratification
          happens INSIDE each fold's date range).
    """
    if len(dates) != len(regime_labels):
        raise ValueError(
            f"dates length ({len(dates)}) != regime_labels length ({len(regime_labels)})"
        )

    rng = np.random.default_rng(seed)
    train_idx: List[int] = []
    test_idx: List[int] = []
    summary: Dict[str, int] = {}

    by_regime: Dict[str, List[int]] = {r: [] for r in REGIME_CLASSES}
    for i, label in enumerate(regime_labels):
        if label in by_regime:
            by_regime[label].append(i)
        # Skip 'unknown' or other labels - not assigned to either set

    for regime, idx_list in by_regime.items():
        n = len(idx_list)
        if n == 0:
            summary[regime] = 0
            summary[f"{regime}_test"] = 0
            summary[f"{regime}_status"] = "INSUFFICIENT_SAMPLE"
            continue

        # Shuffle WITHIN regime for randomness; preserve original chronological
        # order for train/test by sorting after split
        shuffled = idx_list.copy()
        rng.shuffle(shuffled)
        split_at = max(1, int(round(n * train_frac)))
        train_part = sorted(shuffled[:split_at])
        test_part = sorted(shuffled[split_at:])

        summary[regime] = len(train_part)
        summary[f"{regime}_test"] = len(test_part)
        if len(train_part) < min_per_regime or len(test_part) < min_per_regime:
            summary[f"{regime}_status"] = "INSUFFICIENT_SAMPLE"
        else:
            summary[f"{regime}_status"] = "OK"

        train_idx.extend(train_part)
        test_idx.extend(test_part)

    train_idx.sort()
    test_idx.sort()
    return train_idx, test_idx, summary


def regime_proportions(regime_labels: Sequence[str]) -> Dict[str, float]:
    """Return {regime: fraction} over labels (excluding 'unknown')."""
    counts: Dict[str, int] = {r: 0 for r in REGIME_CLASSES}
    total = 0
    for label in regime_labels:
        if label in counts:
            counts[label] += 1
            total += 1
    if total == 0:
        return {r: 0.0 for r in REGIME_CLASSES}
    return {r: c / total for r, c in counts.items()}
