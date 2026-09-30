"""S6-B3128a (B3135): the ONE window every free-level adapter scores on.

WHY. A free-level leg must reproduce the landed family grade before it
grades anything, and the family graders select on the IN-SAMPLE window only
(grade_bollinger_config.py:232 `rc.in_sample(cube)`; the candle grader has
the same design). The candle and bollinger adapters scored EVERY row, so on
a 4-year Step-2 cube they counted the holdout year too: MEASURED on
output_candle_tws_c14_step2, 955 rows per exit against the family's 764 -
the 191 holdout-entered trades. Before the S6-B3120f score gate existed that
leg wrote holdout-contaminated candidate rankings; after it, the leg fails
closed on every Step-2 cube. The institutional adapter already windowed
(grade_free_levels_institutional.py:246, rc.in_sample). This module
makes that the rule for every adapter: the window is roster_core.in_sample
(one definition, L593), applied at load, so an adapter never RECEIVES a
holdout-ENTERED row - not for scoring, not for the signal reproduction
gate, not for any section built on the same frames.

ENTRY-DATED (B3139, S6-B3128a council): the window selects on ENTRY date,
exactly like roster_core.in_sample and every family grader. A trade
entered in-sample that exits inside the holdout IS scored, and its exit
is priced on holdout-period bars - so the true claim is "never scores a
holdout-ENTERED row", never "never reads the holdout". straddle_rows
counts those trades in every window block; whether the program should
exclude them is the owner's convention question (S6-B3139b).
"""
from __future__ import annotations

import pandas as pd

import roster_core as rc


def entry_dates(df: pd.DataFrame) -> pd.Series:
    """datetime.date per row from a raw entry_date column (strings or
    timestamps; the first 10 characters are the calendar date)."""
    return pd.to_datetime(df["entry_date"].astype(str).str[:10]).dt.date


def split_windows(df: pd.DataFrame) -> dict:
    """Row counts per window - in-sample, holdout, outside both."""
    if not len(df):
        return {"in_sample": 0, "holdout": 0, "outside_both": 0}
    d = entry_dates(df)
    is_ = (d >= rc.IS_START) & (d < rc.IS_END)
    ho = (d >= rc.HO_START) & (d < rc.HO_END)
    return {"in_sample": int(is_.sum()), "holdout": int(ho.sum()),
            "outside_both": int((~is_ & ~ho).sum())}


def in_sample_only(df: pd.DataFrame) -> pd.DataFrame:
    """The rows roster_core.in_sample keeps, with the ORIGINAL columns
    untouched (selection by index). Fails closed if anything on or after
    the holdout start survives - the invariant this module exists for."""
    if not len(df):
        return df
    kept = rc.in_sample(df.assign(entry_date=entry_dates(df)))
    out = df.loc[kept.index]
    if len(out) and max(entry_dates(out)) >= rc.HO_START:
        raise ValueError("free_level_window: a row on/after the holdout start "
                         f"{rc.HO_START} survived the in-sample window")
    return out


IS_WINDOW = (rc.IS_START, rc.IS_END)
WINDOW_CONVENTION = ("entry-dated (roster_core.in_sample): a row ENTERED "
                     "in-sample is scored even when it exits inside the "
                     "holdout; straddle_rows counts those rows")


def straddle_count(df: pd.DataFrame) -> dict:
    """Rows ENTERED in-sample whose exit_date is on/after the holdout
    start - scored by the entry-dated window, priced on holdout-period
    bars. `rows` is None when the frame has no exit_date column (not
    measured is never 0 - L580); an in-sample row whose exit_date does
    not parse is counted apart, never silently dropped."""
    if "exit_date" not in df.columns:
        return {"rows": None, "exit_date_unparsed": None}
    if not len(df):
        return {"rows": 0, "exit_date_unparsed": 0}
    d = entry_dates(df)
    x = pd.to_datetime(df["exit_date"].astype(str).str[:10], errors="coerce")
    is_ = ((d >= rc.IS_START) & (d < rc.IS_END)).to_numpy()
    ho = (x >= pd.Timestamp(rc.HO_START)).to_numpy()
    bad = x.isna().to_numpy()
    return {"rows": int((is_ & ho).sum()),
            "exit_date_unparsed": int((is_ & bad).sum())}


def window_disclosure(before: pd.DataFrame, after: pd.DataFrame,
                      label: str) -> dict:
    """The artifact block recording what the window removed."""
    return {"basis": "roster_core.in_sample (the family grader's selector)",
            "in_sample": [str(rc.IS_START), str(rc.IS_END)],
            "frame": label,
            "rows_before_window": split_windows(before),
            "rows_scored": int(len(after)),
            "convention": WINDOW_CONVENTION,
            "straddle_rows": straddle_count(after)}


def window_note(df: pd.DataFrame) -> str:
    """The entry-dated window split of `df` as one string - the shared
    explainer for a reproduction gate whose rows are already narrowed to
    one line (S6-B3139h): a holdout leak and a count drift read differently."""
    w = split_windows(df)
    return (f"rows by entry window: in-sample {w['in_sample']} / "
            f"holdout {w['holdout']} / outside {w['outside_both']}")


def gap_breakdown(ted_all: pd.DataFrame, exit_method: str) -> str:
    """For a reproduction mismatch on one exit: the cube's rows for that
    exit split by window AND by strategy, so the message names the cause
    (a window leak and a rider leak read differently). MEASURED motive:
    S6-B3128a was first misdiagnosed as 'rider-blind' from a bare n gap."""
    g = ted_all[ted_all["exit_method"].astype(str) == str(exit_method)]
    w = split_windows(g)
    by = g["strategy"].astype(str).value_counts().to_dict() if len(g) else {}
    return (f"cube rows for {exit_method}: in-sample {w['in_sample']} / "
            f"holdout {w['holdout']} / outside {w['outside_both']}; "
            f"by strategy {by}")
