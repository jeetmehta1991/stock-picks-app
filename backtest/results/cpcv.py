"""Combinatorial Purged Cross-Validation (CPCV) + Meta-Labeling.

Batch 214 (2026-05-17 owner-approved research review). Two validation
disciplines from the Lopez de Prado *Advances in Financial Machine
Learning* (2018) toolkit, replacing the prior single-path walk-forward
which suffers documented single-path overfit per CPCV theorem (Ch 12).

1. CPCV (cpcv_splits): partitions a time-series sample into N equal
   groups, then generates C(N, k) combinations where k groups serve as
   test set and the other N-k as training. With purging applied to
   remove leak between adjacent samples + embargo to prevent
   information bleed across the boundary. Yields multiple test paths
   for the same total sample, distributing single-path overfit risk
   across the combinatorial structure. Standard parameters: N=6, k=2
   yields 15 distinct paths per Lopez de Prado spec.

2. Meta-labeling (meta_label_classifier_fit + meta_label_predict_proba):
   secondary binary classifier on top of primary trading signals. The
   primary strategy emits a direction; meta-label predicts the
   probability that the trade will be a winner given market features
   (volatility regime, momentum, breadth, etc.). Accept only signals
   with predicted-win-probability above a threshold. Documented Sharpe
   doubling on equity intraday work (Hudson & Thames "Does Meta-Labeling
   Add to Signal Efficacy?" 2022). Lightweight implementation using
   sklearn's GradientBoosting classifier; fallback to logistic
   regression when GBM unavailable.

Both modules are validation-time tools (run on closed-trades log to
audit / re-rank), not entry-time engine plumbing. They produce reports
that owner-facing dashboards consume.
"""

from __future__ import annotations

from itertools import combinations
from typing import Iterator, List, Optional, Tuple

import numpy as np
import pandas as pd


def cpcv_splits(
    n_samples: int,
    n_groups: int = 6,
    n_test_groups: int = 2,
    embargo_pct: float = 0.01,
) -> Iterator[Tuple[List[int], List[int]]]:
    """Yield (train_indices, test_indices) for each combinatorial path.

    Lopez de Prado 2018 Ch 12 algorithm:
      1. Split [0, n_samples) into n_groups equal contiguous chunks
      2. For each combination of n_test_groups chunks (test set):
           - Train set = all other chunks (concatenated)
           - Apply embargo: remove training samples within embargo_pct of
             the test-set boundaries (prevents information bleed)
      3. Yield (train_idx, test_idx)

    Total paths = C(n_groups, n_test_groups). Default 6 groups choose 2
    -> 15 paths per Lopez de Prado canonical spec. Larger n_groups gives
    more paths but smaller test sets.

    Args:
      n_samples:     total observations (typically rows in trade log
                     after chronological sort)
      n_groups:      contiguous chunks (default 6)
      n_test_groups: test chunks per combination (default 2)
      embargo_pct:   training-side embargo around test boundaries
                     (default 1%); set 0.0 to disable
    """
    if n_samples <= 0 or n_groups < 2 or n_test_groups < 1 or n_test_groups >= n_groups:
        return
    # Compute group boundaries
    boundaries = np.linspace(0, n_samples, n_groups + 1, dtype=int)
    embargo = max(1, int(n_samples * embargo_pct))
    for test_combo in combinations(range(n_groups), n_test_groups):
        test_idx: List[int] = []
        excluded_zones: List[Tuple[int, int]] = []
        for g in test_combo:
            start, end = int(boundaries[g]), int(boundaries[g + 1])
            test_idx.extend(range(start, end))
            # Embargo zone extends `embargo` samples beyond each end
            excluded_zones.append((max(0, start - embargo), min(n_samples, end + embargo)))
        # Train = all samples NOT in test AND NOT in embargo zones
        train_idx: List[int] = []
        for i in range(n_samples):
            if i in test_idx:
                continue
            in_embargo = any(z_start <= i < z_end for z_start, z_end in excluded_zones)
            if in_embargo:
                continue
            train_idx.append(i)
        yield train_idx, test_idx


def cpcv_summary(
    n_samples: int,
    n_groups: int = 6,
    n_test_groups: int = 2,
    embargo_pct: float = 0.01,
) -> dict:
    """Compute summary statistics for a CPCV configuration."""
    paths = list(cpcv_splits(n_samples, n_groups, n_test_groups, embargo_pct))
    if not paths:
        return {
            "n_paths": 0, "n_samples": n_samples,
            "avg_train_size": 0, "avg_test_size": 0,
        }
    train_sizes = [len(t) for t, _ in paths]
    test_sizes  = [len(t) for _, t in paths]
    return {
        "n_paths":        len(paths),
        "n_samples":      n_samples,
        "n_groups":       n_groups,
        "n_test_groups":  n_test_groups,
        "embargo_pct":    embargo_pct,
        "avg_train_size": round(float(np.mean(train_sizes)), 2),
        "avg_test_size":  round(float(np.mean(test_sizes)), 2),
        "min_train_size": min(train_sizes),
        "max_train_size": max(train_sizes),
    }


def meta_label_classifier_fit(
    features: pd.DataFrame,
    labels: pd.Series,
    method: str = "auto",
    random_state: int = 42,
):
    """Fit a binary classifier (win/loss prediction) for meta-labeling.

    Lopez de Prado 2017 / Hudson & Thames 2022. Features should be
    market-context columns (volatility, regime, breadth, etc.) plus
    optionally the primary strategy signal itself. Labels are
    1=winning trade, 0=losing trade (binary).

    Batch 228 (housekeeping 2026-05-18 owner-approved): XGBoost upgrade
    per Joubert-Snyman 2024 - tree-based methods (especially XGBoost)
    outperform sklearn GBM on time-series meta-labeling features.
    Preference order: xgboost -> sklearn GBM -> sklearn logreg. Each
    fallback fires when the preferred library is unavailable.

    Args:
      features:    DataFrame, rows = trades, cols = numeric features
      labels:      Series of {0, 1}, same length as features
      method:      "xgb" | "gbm" | "logreg" | "auto"
                   "auto": try xgboost, then sklearn GBM, then logreg
      random_state: RNG seed for reproducibility

    Returns the fitted classifier. None if all backends unavailable
    or inputs degenerate.
    """
    if features is None or features.empty or labels is None or len(labels) == 0:
        return None
    if len(features) != len(labels):
        return None
    try:
        # Drop rows with any NaN to avoid backend errors; production
        # should impute upstream
        clean = pd.concat([features.reset_index(drop=True),
                           labels.reset_index(drop=True).rename("__y__")], axis=1).dropna()
        if clean.empty or clean["__y__"].nunique() < 2:
            return None
        X = clean.drop(columns=["__y__"])
        y = clean["__y__"].astype(int)
        if method == "logreg":
            from sklearn.linear_model import LogisticRegression
            clf = LogisticRegression(random_state=random_state, max_iter=500)
        elif method == "gbm":
            try:
                from sklearn.ensemble import GradientBoostingClassifier
                clf = GradientBoostingClassifier(
                    n_estimators=100, max_depth=3, random_state=random_state,
                )
            except ImportError:
                return None
        elif method == "xgb":
            try:
                import xgboost as _xgb
                clf = _xgb.XGBClassifier(
                    n_estimators=100, max_depth=3,
                    learning_rate=0.1, random_state=random_state,
                    eval_metric="logloss", verbosity=0,
                )
            except ImportError:
                return None
        else:  # auto: xgb -> gbm -> logreg
            try:
                import xgboost as _xgb
                clf = _xgb.XGBClassifier(
                    n_estimators=100, max_depth=3,
                    learning_rate=0.1, random_state=random_state,
                    eval_metric="logloss", verbosity=0,
                )
            except ImportError:
                try:
                    from sklearn.ensemble import GradientBoostingClassifier
                    clf = GradientBoostingClassifier(
                        n_estimators=100, max_depth=3, random_state=random_state,
                    )
                except ImportError:
                    from sklearn.linear_model import LogisticRegression
                    clf = LogisticRegression(random_state=random_state, max_iter=500)
        clf.fit(X, y)
        return clf
    except Exception:
        return None


def compute_pbo_cscv(
    perf_matrix: pd.DataFrame,
    n_partitions: int = 16,
) -> dict:
    """Probability of Backtest Overfitting (PBO) via Combinatorially
    Symmetric Cross-Validation (CSCV).

    Batch 221 (validation 2026-05-18 owner-approved research review).
    Source: Bailey-Borwein-Lopez de Prado-Zhu 2017 *Journal of
    Computational Finance* "The probability of backtest overfitting".

    Mechanism:
      1. Partition the time axis of perf_matrix (rows=periods,
         cols=strategies) into S equal contiguous chunks
      2. For each combination of S/2 chunks (IS) vs S/2 chunks (OOS):
         a. Identify the IS-best strategy (highest mean return)
         b. Compute its OOS rank vs the strategy population
         c. Compute logit of OOS-rank-percentile (0=worst, 1=best)
      3. PBO = P(IS-winner is below OOS median) = fraction of paths
         where IS-best has OOS rank <= 50th percentile

    Interpretation:
      - PBO < 0.5  -> roster is not overfit (IS winners tend to OOS-win)
      - PBO >= 0.5 -> roster is overfit (IS winners are no better than
                     random OOS); strategy selection process is broken
      - PBO ~= 1.0 -> SEVERELY overfit

    Inputs:
      perf_matrix: DataFrame indexed by date with strategy returns as
        columns. Period returns (daily / weekly / monthly OK).
      n_partitions: number of CSCV partitions (default 16, paper
        recommended). Must be even; will be coerced.

    Returns dict:
      - pbo:            float in [0, 1] (lower is better)
      - n_combinations: int (number of IS/OOS combinations evaluated)
      - logits:         list of OOS-rank-logit values
      - interpretation: string interpretation
      - verdict:        "ok" / "warning" / "overfit"

    Returns {"pbo": None, ...} on insufficient data.
    """
    if perf_matrix is None or perf_matrix.empty:
        return {"pbo": None, "n_combinations": 0, "logits": [],
                "interpretation": "empty_input", "verdict": "n/a"}
    n_strategies = perf_matrix.shape[1]
    if n_strategies < 2:
        return {"pbo": None, "n_combinations": 0, "logits": [],
                "interpretation": "single_strategy", "verdict": "n/a"}
    n_periods = perf_matrix.shape[0]
    if n_periods < n_partitions:
        return {"pbo": None, "n_combinations": 0, "logits": [],
                "interpretation": "insufficient_periods", "verdict": "n/a"}
    # Coerce n_partitions to even
    if n_partitions % 2 != 0:
        n_partitions += 1
    # Partition rows into n_partitions chunks
    chunk_size = n_periods // n_partitions
    if chunk_size < 1:
        return {"pbo": None, "n_combinations": 0, "logits": [],
                "interpretation": "chunks_too_small", "verdict": "n/a"}
    chunks = [
        perf_matrix.iloc[i * chunk_size: (i + 1) * chunk_size]
        for i in range(n_partitions)
    ]
    # Iterate combinations of S/2 IS chunks
    half = n_partitions // 2
    logits = []
    below_median_count = 0
    total_count = 0
    from itertools import combinations
    for is_chunks_idx in combinations(range(n_partitions), half):
        is_chunks_idx_set = set(is_chunks_idx)
        oos_chunks_idx = [i for i in range(n_partitions) if i not in is_chunks_idx_set]
        is_df  = pd.concat([chunks[i] for i in is_chunks_idx])
        oos_df = pd.concat([chunks[i] for i in oos_chunks_idx])
        if is_df.empty or oos_df.empty:
            continue
        # Strategy mean returns IS + OOS
        is_means  = is_df.mean()
        oos_means = oos_df.mean()
        if is_means.empty or oos_means.empty:
            continue
        # IS-best strategy (highest mean)
        try:
            is_winner = is_means.idxmax()
        except Exception:
            continue
        if pd.isna(is_winner) or is_winner not in oos_means.index:
            continue
        # OOS rank of IS-winner (1 = lowest, n = highest)
        oos_ranks = oos_means.rank(method="average")
        winner_rank = float(oos_ranks[is_winner])
        # Rank percentile (0..1)
        oos_pctile = (winner_rank - 0.5) / len(oos_means)
        oos_pctile = max(min(oos_pctile, 0.999), 0.001)  # avoid log(0)
        # Logit
        try:
            import math
            logit = math.log(oos_pctile / (1.0 - oos_pctile))
            logits.append(logit)
        except Exception:
            pass
        if winner_rank <= len(oos_means) / 2.0:
            below_median_count += 1
        total_count += 1
    if total_count == 0:
        return {"pbo": None, "n_combinations": 0, "logits": [],
                "interpretation": "no_valid_combinations", "verdict": "n/a"}
    pbo = below_median_count / total_count
    if pbo < 0.4:
        verdict = "ok"
        interp = "roster_not_overfit"
    elif pbo < 0.6:
        verdict = "warning"
        interp = "borderline_overfit"
    else:
        verdict = "overfit"
        interp = "roster_overfit"
    return {
        "pbo":            round(pbo, 4),
        "n_combinations": total_count,
        "logits":         [round(l, 4) for l in logits[:50]],  # cap for storage
        "interpretation": interp,
        "verdict":        verdict,
    }


def meta_label_predict_proba(clf, features: pd.DataFrame) -> Optional[np.ndarray]:
    """Predict win-probability for each row in features. Returns None on
    error or when clf is None."""
    if clf is None or features is None or features.empty:
        return None
    try:
        proba = clf.predict_proba(features)
        # Returns shape (N, 2) with columns [P(0), P(1)]; we want P(win)
        return proba[:, 1]
    except Exception:
        return None
