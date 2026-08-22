# -*- coding: utf-8 -*-
"""Render a value that might not have been measured (B1899 / L580).

TWICE IN TWO BATCHES a renderer printed a number for something nobody
measured:

    B1889b  audit_ticket_staleness.main() formatted None with {n:>4} and
            CRASHED. Fixed to print `n/a`.
    B1898   table_c() printed `0` for a `bands` value the artifact does not
            record. `0 bands` reads as "tested nothing"; the truth was "not
            recorded".

The crash was the lucky one - it stopped. The `0` would have been read.

**A missing measurement and a measured zero are different facts, and only one
of them is evidence.** This is the single place that decides how the first is
shown, so the rule travels with the helper instead of being re-learned per
renderer (L536).
"""
from __future__ import annotations

MISSING = "-"


def fmt(value, *, missing: str = MISSING, spec: str = "") -> str:
    """`value` rendered, or `missing` when it was never measured.

    `None` means NOT MEASURED. A real zero renders as `0`, because a measured
    zero IS evidence and must not be hidden behind the same token as an
    absence.
    """
    if value is None:
        return missing
    if spec:
        try:
            return format(value, spec)
        except (TypeError, ValueError):
            return str(value)
    return str(value)


def fmt_cell(value, *, width: int = 0) -> str:
    """Table-cell form: right-aligned to `width` when one is given."""
    s = fmt(value)
    return f"{s:>{width}}" if width else s
