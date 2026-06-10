"""B688 regression-guard tests for the T1/T2 MACD docstring honesty fix
(EXECUTION_QUEUE ticket S4-B687-T1-T2-MACD-DEFINITION-DOCSTRING-FIX).

Pre-B688 the T1 (`strat_macd_crossover`) and T2 (`strat_macd_fast_crossover`)
`_strat3` bullets described "MACD 12/26/9 crossed above zero -- momentum
turning positive" which is the CENTERLINE-cross semantic (MACD line crosses
zero). The producer at technical.py:558 computes
`crossover_up = (mh > 0 and pmh <= 0)` where `mh = histogram = MACD_line -
signal_line`. Histogram sign change = SIGNAL-LINE cross (MACD line crossed
above/below signal line), NOT centerline cross.

B687 reviewer Finding #3 caught the mismatch. B688 shipped the docstring
honesty fix.

These tests pin the fix so a future edit cannot silently revert to the
pre-B688 centerline-cross language. Code is correct + unchanged; only the
docstrings/bullets are updated.

Pyramid coverage: 6 pins covering (a) screener.py T1 bullet language,
(b) screener.py T2 bullet language, (c) walk-doc B687 banner Finding #3
status update, (d) walk-doc T1 Step 1 + Step 4 language, (e) walk-doc T2
Step 1 + Step 4 language, (f) execution-queue ticket RESOLVED-B688 closure.
"""
from __future__ import annotations

import inspect
from pathlib import Path

from backtest.signals import screener


def _source_lines(func) -> str:
    """Return the source code of a strategy function as a string."""
    return inspect.getsource(func)


# ---------------------------------------------------------------------------
# Pin 1: T1 strat_macd_crossover bullets must say "signal-line cross"
# ---------------------------------------------------------------------------
def test_b688_pin1_t1_macd_crossover_bullets_say_signal_line_cross():
    """T1 LONG + SHORT bullets must reference signal-line cross / histogram
    sign change semantics (NOT centerline / 'crossed above zero')."""
    src = _source_lines(screener.strat_macd_crossover)
    assert "signal-line cross up" in src, (
        "B688 fix lost: T1 LONG bullet must say 'signal-line cross up'"
    )
    assert "signal-line cross down" in src, (
        "B688 fix lost: T1 SHORT bullet must say 'signal-line cross down'"
    )
    assert "histogram sign change" in src, (
        "B688 fix lost: T1 bullets must reference 'histogram sign change'"
    )


# ---------------------------------------------------------------------------
# Pin 2: T1 must NOT contain the pre-B688 centerline-cross language
# ---------------------------------------------------------------------------
def test_b688_pin2_t1_macd_crossover_no_centerline_language():
    """The pre-B688 'crossed above zero' / 'crossed below zero' centerline
    language must not reappear in T1 bullets."""
    src = _source_lines(screener.strat_macd_crossover)
    assert "crossed above zero" not in src, (
        "B688 regression: T1 reverted to pre-B688 centerline-cross language. "
        "Producer fires on signal-line cross (histogram sign change), not "
        "centerline cross. See ticket S4-B687-T1-T2-MACD-DEFINITION-DOCSTRING-FIX."
    )
    assert "crossed below zero" not in src, (
        "B688 regression: T1 reverted to pre-B688 centerline-cross language."
    )
    assert "momentum turning positive" not in src, (
        "B688 regression: T1 reverted to pre-B688 centerline-cross semantic "
        "('momentum turning positive'). Signal-line cross is 'momentum "
        "accelerating', not 'momentum turning positive' (which describes "
        "centerline cross)."
    )
    assert "momentum turning negative" not in src, (
        "B688 regression: T1 reverted to pre-B688 centerline-cross semantic."
    )


# ---------------------------------------------------------------------------
# Pin 3: T2 strat_macd_fast_crossover bullets must say "signal-line cross"
# ---------------------------------------------------------------------------
def test_b688_pin3_t2_macd_fast_crossover_bullets_say_signal_line_cross():
    """T2 LONG + SHORT bullets must reference signal-line cross + 'early
    momentum acceleration' (NOT 'early momentum shift')."""
    src = _source_lines(screener.strat_macd_fast_crossover)
    assert "signal-line cross up" in src, (
        "B688 fix lost: T2 LONG bullet must say 'signal-line cross up'"
    )
    assert "signal-line cross down" in src, (
        "B688 fix lost: T2 SHORT bullet must say 'signal-line cross down'"
    )
    assert "histogram sign change" in src, (
        "B688 fix lost: T2 bullets must reference 'histogram sign change'"
    )
    assert "early momentum acceleration" in src, (
        "B688 fix lost: T2 should describe 'early momentum acceleration' "
        "(signal-line cross accelerates existing momentum) not 'early "
        "momentum shift' (which implies centerline-cross direction change)."
    )


# ---------------------------------------------------------------------------
# Pin 4: T2 must NOT contain the pre-B688 centerline-cross language
# ---------------------------------------------------------------------------
def test_b688_pin4_t2_macd_fast_crossover_no_centerline_language():
    src = _source_lines(screener.strat_macd_fast_crossover)
    assert "crossed above zero" not in src, (
        "B688 regression: T2 reverted to pre-B688 centerline-cross language."
    )
    assert "crossed below zero" not in src, (
        "B688 regression: T2 reverted to pre-B688 centerline-cross language."
    )


# ---------------------------------------------------------------------------
# Pin 5: STAGE_4_TREND_CLUSTER_WALKS.md B687 banner Finding #3 status closed
# ---------------------------------------------------------------------------
def test_b688_pin5_trend_walk_doc_b687_banner_finding3_closed():
    """The B687 banner row for Finding #3 must show FIXED B688 status, not
    the pre-B688 VERIFIED B687 status."""
    doc = Path(__file__).resolve().parents[2] / "STAGE_4_TREND_CLUSTER_WALKS.md"
    text = doc.read_text(encoding="utf-8")
    # The line is the Finding #3 row in the banner table.
    assert "FIXED B688" in text, (
        "B688 fix lost: STAGE_4_TREND_CLUSTER_WALKS.md B687 banner Finding "
        "#3 row must show FIXED B688 status."
    )


# ---------------------------------------------------------------------------
# Pin 6: STAGE_4_TREND_CLUSTER_WALKS.md T1/T2 walk-sections updated
# ---------------------------------------------------------------------------
def test_b688_pin6_trend_walk_doc_t1_t2_sections_say_signal_line_cross():
    """T1 + T2 walk sections must show signal-line cross language (mirroring
    the screener.py fix) so a reader of the walk doc sees the corrected
    semantics. The pre-B688 'crossed above zero' language in T1 + T2 code
    blocks must be replaced."""
    doc = Path(__file__).resolve().parents[2] / "STAGE_4_TREND_CLUSTER_WALKS.md"
    text = doc.read_text(encoding="utf-8")

    # The walk doc shows T1 Step 1 code block mirroring screener.py. Both
    # the code mirror and the gate-table rows should reference signal-line.
    assert text.count("signal-line cross") >= 4, (
        "B688 fix lost: STAGE_4_TREND_CLUSTER_WALKS.md must contain >=4 "
        "occurrences of 'signal-line cross' across T1 + T2 walk sections "
        "(code mirror + gate table + Step 3 producer-source + Step 4 "
        "doc-vs-thesis)."
    )
    # The Finding #3 banner row + T1 Step 4 + T2 Step 4 references to the
    # PRE-B688 centerline-cross language are allowed (they explain what was
    # changed). But the T1 + T2 CODE MIRRORS must NOT contain the pre-B688
    # bullets verbatim.
    pre_b688_t1_bullet = (
        '"MACD 12/26/9 crossed above zero  -  momentum turning positive"'
    )
    pre_b688_t2_bullet = (
        '"Fast MACD 8/21/5 crossed above zero  -  early momentum shift bullish"'
    )
    assert pre_b688_t1_bullet not in text, (
        "B688 regression: T1 code mirror in walk doc reverted to pre-B688 "
        "centerline-cross bullet."
    )
    assert pre_b688_t2_bullet not in text, (
        "B688 regression: T2 code mirror in walk doc reverted to pre-B688 "
        "centerline-cross bullet."
    )


# ---------------------------------------------------------------------------
# Pin 7: EXECUTION_QUEUE.md ticket marked RESOLVED-B688
# ---------------------------------------------------------------------------
def test_b688_pin7_execution_queue_ticket_resolved():
    """The S4-B687-T1-T2-MACD-DEFINITION-DOCSTRING-FIX ticket row must show
    RESOLVED-B688 status, not PENDING-DOCSTRING-FIX."""
    queue = Path(__file__).resolve().parents[2] / "EXECUTION_QUEUE.md"
    text = queue.read_text(encoding="utf-8")
    # Find the ticket line.
    ticket_lines = [
        line for line in text.splitlines()
        if "S4-B687-T1-T2-MACD-DEFINITION-DOCSTRING-FIX" in line
    ]
    assert ticket_lines, (
        "EXECUTION_QUEUE.md missing the S4-B687-T1-T2-MACD-DEFINITION-DOCSTRING-FIX ticket row"
    )
    # The ticket should now be RESOLVED-B688, not PENDING-DOCSTRING-FIX.
    line = ticket_lines[0]
    assert "RESOLVED-B688" in line, (
        f"B688 fix lost: ticket row must contain 'RESOLVED-B688' status. Got: {line[:200]}"
    )
    assert "PENDING-DOCSTRING-FIX" not in line, (
        "B688 regression: ticket reverted to PENDING-DOCSTRING-FIX. "
        "Should be RESOLVED-B688."
    )


# ---------------------------------------------------------------------------
# Pin 8: Producer behavior unchanged - T1/T2 strategies still fire identically
# ---------------------------------------------------------------------------
def test_b688_pin8_producer_behavior_unchanged_signal_line_cross():
    """B688 was a docstring-only fix. The strategy must still fire on
    `macd_12_26_9_crossover_up` LONG and `_crossover_dn` SHORT, exactly as
    pre-B688. Behavior identical; only the human-facing bullet changed.

    `_strat3` returns a dict with keys: fires, direction, category,
    signals_used, context_bullets."""
    # LONG fires
    s_long = {"macd_12_26_9_crossover_up": True}
    result = screener.strat_macd_crossover(s_long)
    assert result["fires"] is True
    assert result["direction"] == "long", (
        "B688 broke T1: LONG should still fire on macd_12_26_9_crossover_up=True. "
        "B688 was supposed to be docstring-only."
    )

    # SHORT fires (no borrow-trap signal in dict so SM-5 gate is dormant)
    s_short = {"macd_12_26_9_crossover_dn": True}
    result = screener.strat_macd_crossover(s_short)
    assert result["fires"] is True
    assert result["direction"] == "short", (
        "B688 broke T1: SHORT should still fire on macd_12_26_9_crossover_dn=True."
    )

    # No fire when neither set
    s_none = {}
    result = screener.strat_macd_crossover(s_none)
    assert result["fires"] is False, "B688 broke T1: no-signal case should not fire"
    assert result["direction"] is None


def test_b688_pin9_t2_producer_behavior_unchanged():
    """T2 (`strat_macd_fast_crossover`) parallel to Pin 8 for T2's MACD(8,21,5)
    producer signals."""
    s_long = {"macd_8_21_5_crossover_up": True}
    result = screener.strat_macd_fast_crossover(s_long)
    assert result["fires"] is True
    assert result["direction"] == "long", "B688 broke T2 LONG fire"

    s_short = {"macd_8_21_5_crossover_dn": True}
    result = screener.strat_macd_fast_crossover(s_short)
    assert result["fires"] is True
    assert result["direction"] == "short", "B688 broke T2 SHORT fire"


# ---------------------------------------------------------------------------
# Pin 10: Producer-level invariant - histogram sign change defines crossover
# ---------------------------------------------------------------------------
def test_b688_pin10_producer_invariant_histogram_sign_change():
    """Document via runtime check that the technical.py producer uses
    histogram sign change for crossover_up. If this ever changes (e.g.
    someone swaps to centerline-cross detection), the strategy semantics
    change and B688's docstring becomes wrong again."""
    # Read the producer source directly to confirm the relevant line.
    from backtest.signals import technical as tech
    src = inspect.getsource(tech.compute_macd)
    assert "mh > 0 and pmh <= 0" in src, (
        "Producer compute_macd no longer uses 'mh > 0 and pmh <= 0' for "
        "crossover_up. If the producer changed to centerline-cross detection "
        "(e.g. 'ml > 0 and pml <= 0'), B688's signal-line-cross docstring "
        "is now WRONG and must be updated. See S4-B687-T1-T2-MACD-DEFINITION-"
        "DOCSTRING-FIX ticket history."
    )
    assert "mh < 0 and pmh >= 0" in src, (
        "Producer compute_macd no longer uses 'mh < 0 and pmh >= 0' for "
        "crossover_dn. Same B688-docstring-correctness implication."
    )
