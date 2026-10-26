#!/usr/bin/env python
"""scripts/episode_disclosure.py - S6-B3315 (B3139q-r119): the one-episode
disclosure every Step-1 search writes beside its ranking key.

A Step-1 search prices its best cell against a permutation null that shuffles
signal magnitudes ACROSS fires. That prices the ASSOCIATION between a level
and the outcome, and it cannot see whether the association is a trade
characteristic or ONE market episode - a count that only grows, or a macro
level, is a time proxy and selects a date. MEASURED on squeeze_breakout's
breadth grid (S6-B3248, output_audit/b3248_squeeze_breakout_breadth_episode_check.json):
the four top in-sample cells put 83.2 to 97.5 pct of their trades in April
2025 and kept 5 to 32 trades without it, while the null priced the best cell
at p 0.0099.

month_concentration(rows, score) answers, for ONE (cell, exit)'s in-sample
trades: which calendar month holds the most of them, its share, how many
months the trades span, and the cell's IS Sharpe without that month - scored
by the CALLER's own row scorer, None below its power floor, never 0 (L580).
ONE definition (L593): breadth_step1_grid and offline_level_sweep call it
inside their grading loops, and table_d_render reads what they wrote. A
disclosure, not a gate: it changes no verdict and no cell set (#310).
"""
from __future__ import annotations

import pandas as pd

# CHOSEN (#165): the Table D preamble names a row whose largest month holds MORE
# THAN HALF its in-sample trades. The artifact keeps the share itself, so any
# reader can draw another line; this one is the plain-language 'most of it'.
SHARE_FLAG = 0.5


def month_concentration(rows: pd.DataFrame, score) -> dict | None:
    """The month concentration of one (cell, exit)'s in-sample trades, or None
    for an empty frame. `score` is the CALLER's own row scorer - a function of
    a trade frame returning its IS Sharpe, or None below the caller's power
    floor - so the Sharpe without the top month is scored exactly as the
    row's ranking key, on the caller's pnl basis. This module never scores a
    trade itself: test_b3122's census classifies the CALLER, which owns the
    basis (pinned by test_b3315). Ties on the largest count resolve to the
    EARLIEST month (sorted, stable), so the disclosure is deterministic."""
    if rows is None or len(rows) == 0:
        return None
    months = pd.Series([str(d)[:7] for d in rows["entry_date"]], index=rows.index)
    vc = months.value_counts().sort_index().sort_values(ascending=False, kind="stable")
    top, n_top = str(vc.index[0]), int(vc.iloc[0])
    rest = rows[months != top]
    return {"top_month": top, "top_month_share": round(n_top / len(rows), 3),
            "months": int(vc.size), "n": int(len(rows)),
            "n_without_top_month": int(len(rest)),
            "is_sharpe_without_top_month": (score(rest) if len(rest) else None)}
