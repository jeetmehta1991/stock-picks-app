# -*- coding: utf-8 -*-
"""Searches that cannot report a false absence (B1862 / L568).

MEASURED: watching a 200-ticker run for fires with `[0-9]+/200 passed` returned
nothing, and I reported "still in warmup" twice. The screener's denominator is
the PIT-ACTIVE universe - 185, not the file's 200 - so the run had been firing
the whole time, and the monitor carried the same pattern and would have said
"no fires" every 11 minutes, unattended.

**An empty result is indistinguishable from a wrong pattern**, exactly as a
silent gate is indistinguishable from a working one (L561). The only thing that
separates them is a POSITIVE CONTROL: a string the pattern MUST match.
"""
from __future__ import annotations

import re


class PatternNeverMatched(AssertionError):
    """The pattern failed its positive control, so absence proves nothing."""


def search_with_control(pattern: str, haystack: str, control: str,
                        *, flags: int = 0) -> list[str]:
    """All matches of `pattern` in `haystack`, or raise if the pattern is wrong.

    `control` is a string the pattern MUST match - typically one real line
    copied out of the data being searched. If the pattern does not match the
    control, the pattern is broken and an empty result would be a lie, so this
    raises rather than returning [].

    Returns [] only when the pattern is PROVEN able to match and the haystack
    genuinely contains nothing.
    """
    rx = re.compile(pattern, flags)
    if not rx.search(control):
        raise PatternNeverMatched(
            f"pattern {pattern!r} does not match its positive control "
            f"{control[:120]!r}. An empty result would be indistinguishable "
            "from this wrong pattern - fix the pattern or supply a control "
            "that reflects the real data (L568).")
    return rx.findall(haystack)


def absent(pattern: str, haystack: str, control: str, *, flags: int = 0) -> bool:
    """True only when the pattern is proven able to match and found nothing."""
    return not search_with_control(pattern, haystack, control, flags=flags)
