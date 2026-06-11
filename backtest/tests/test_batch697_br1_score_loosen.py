"""B697 regression-guard tests for the BR-1 (`strat_52w_high_breakout`)
score-of-N loosen + sector_outperforming_spy gate removal.

Owner-approved 2026-06-11 per [B693 sweep results](output_audit/b693_sweeps/b693_sweeps_report.md):
  - Sweep 1: 4-way AND (pre-B697) fires 0.9/ticker-year; 3-of-4 score
    gives 13.9/ticker-year = 15.9x more fires
  - Add-test 4: sector_outperforming_spy is REJECT_REDUNDANT (-0.6pp FT
    drop with no lift)

Pre-B697 config (5-AND): break_52w_high + vol_spike_17x +
sector_outperforming_spy + close_above_open + close_in_top_40pct_of_range
all required on the same bar.

Post-B697 config (require break + 2-of-3 score):
  REQUIRE: break_52w_high (the EVENT)
  AND >= 2 of: (vol_spike_17x, close_above_open, close_in_top_40pct_of_range)

Anti-fakeout parameters (break-clearance margin, immediate-reclaim) are
DEFERRED to B698 -- they need new producer signals.
"""
from __future__ import annotations

from backtest.signals.screener import strat_52w_high_breakout


def _fires(sig: dict) -> bool:
    return bool(strat_52w_high_breakout(sig).get("fires"))


# ---------------------------------------------------------------------------
# Pin 1: Without break_52w_high, the strategy NEVER fires (event required)
# ---------------------------------------------------------------------------
def test_b697_pin1_break_event_is_required():
    """No 52w-high breakout EVENT -> no fire. The score-of-N only relaxes
    the confirmations, never the event itself."""
    sig = {"vol_spike_17x": True, "close_above_open": True,
           "close_in_top_40pct_of_range": True}
    assert not _fires(sig), "Strategy must require break_52w_high as the trigger event"


# ---------------------------------------------------------------------------
# Pin 2: Break + 0 confirmations does NOT fire
# ---------------------------------------------------------------------------
def test_b697_pin2_break_alone_no_confirmations_does_not_fire():
    assert not _fires({"break_52w_high": True})


# ---------------------------------------------------------------------------
# Pin 3: Break + 1 of 3 does NOT fire (need 2+)
# ---------------------------------------------------------------------------
def test_b697_pin3_break_plus_1_confirmation_does_not_fire():
    for confirm in ["vol_spike_17x", "close_above_open", "close_in_top_40pct_of_range"]:
        sig = {"break_52w_high": True, confirm: True}
        assert not _fires(sig), f"Break + only {confirm} should not fire (need 2-of-3 score)"


# ---------------------------------------------------------------------------
# Pin 4: Break + 2 of 3 confirmations FIRES (any 2)
# ---------------------------------------------------------------------------
def test_b697_pin4_break_plus_2_of_3_fires():
    pairs = [
        ("vol_spike_17x", "close_above_open"),
        ("vol_spike_17x", "close_in_top_40pct_of_range"),
        ("close_above_open", "close_in_top_40pct_of_range"),
    ]
    for a, b in pairs:
        sig = {"break_52w_high": True, a: True, b: True}
        assert _fires(sig), f"Break + {a} + {b} (2-of-3 score) must fire"


# ---------------------------------------------------------------------------
# Pin 5: Break + 3 of 3 confirmations fires (regression: still fires)
# ---------------------------------------------------------------------------
def test_b697_pin5_break_plus_all_3_still_fires():
    sig = {"break_52w_high": True, "vol_spike_17x": True,
           "close_above_open": True, "close_in_top_40pct_of_range": True}
    assert _fires(sig)


# ---------------------------------------------------------------------------
# Pin 6: sector_outperforming_spy is now IGNORED (gate dropped)
# ---------------------------------------------------------------------------
def test_b697_pin6_sector_outperforming_spy_is_ignored():
    """Pre-B697 would require sector_outperforming_spy=True for any fire.
    Post-B697 the gate is dropped; sector_outperforming_spy=True has no
    effect (does NOT contribute to the 2-of-3 score)."""
    # Sector gate alone -- should NOT fire (no break event)
    assert not _fires({"sector_outperforming_spy": True})
    # Break + sector ONLY (no other confirmations) -- should NOT fire
    assert not _fires({"break_52w_high": True, "sector_outperforming_spy": True})
    # Break + 1 confirmation + sector_outperforming_spy -- should NOT fire
    # (sector_outperforming_spy not counted in the score)
    sig = {"break_52w_high": True, "vol_spike_17x": True,
           "sector_outperforming_spy": True}
    assert not _fires(sig), (
        "sector_outperforming_spy must NOT count toward the 2-of-3 score "
        "(gate dropped per reviewer Finding #6 / B693 sweep 4 REJECT_REDUNDANT)"
    )


# ---------------------------------------------------------------------------
# Pin 7: Source-code regression - no s.get('sector_outperforming_spy') in body
# ---------------------------------------------------------------------------
def test_b697_pin7_sector_gate_not_in_source():
    """Source-read guard: the dropped gate must not reappear in the
    strategy body via copy-paste regression."""
    import inspect
    src = inspect.getsource(strat_52w_high_breakout)
    # Allow the docstring to mention the dropped gate (it's part of the
    # rationale), but the function body must not read it via s.get(...)
    body = src.split('"""')[2] if src.count('"""') >= 2 else src
    assert 's.get("sector_outperforming_spy")' not in body, (
        "B697 regression: sector_outperforming_spy gate reappeared in the "
        "strategy body. Drop per reviewer Finding #6."
    )


# ---------------------------------------------------------------------------
# Pin 8: signals_used metadata excludes the dropped gate
# ---------------------------------------------------------------------------
def test_b697_pin8_signals_used_excludes_sector_gate():
    """The signals_used metadata list (used by the cube + dashboards) must
    not advertise sector_outperforming_spy as a gate."""
    result = strat_52w_high_breakout({"break_52w_high": True, "vol_spike_17x": True,
                                       "close_above_open": True})
    used = result.get("signals_used", [])
    assert "sector_outperforming_spy" not in used, (
        "signals_used must not advertise sector_outperforming_spy post-B697 drop"
    )


# ---------------------------------------------------------------------------
# Pin 9: Fire count signature: break + 2-of-3 fires more often than 4-AND
# ---------------------------------------------------------------------------
def test_b697_pin9_score_of_n_fires_more_than_4_and():
    """Hypothesis ground-truth: across 8 example signal dicts, the
    score-of-2-of-3 (post-B697) must fire on a STRICT SUPERSET of cases
    where the pre-B697 4-AND (break + vol + above + top) would have fired.

    Sweep 1 result: 4-AND = 131 fires (0.9/ticker-yr); score-of-N = 2078
    fires (13.9/ticker-yr) on a sample of 30 tickers x 5 years.
    """
    cases = [
        # (signals, fires_under_4_AND, fires_under_score_2_of_3)
        ({"break_52w_high": True, "vol_spike_17x": True, "close_above_open": True, "close_in_top_40pct_of_range": True}, True, True),
        # Break + vol + above (missing top_40): 4-AND False, score True (2-of-3)
        ({"break_52w_high": True, "vol_spike_17x": True, "close_above_open": True}, False, True),
        # Break + vol + top (missing above): 4-AND False, score True (2-of-3)
        ({"break_52w_high": True, "vol_spike_17x": True, "close_in_top_40pct_of_range": True}, False, True),
        # Break + above + top (missing vol): 4-AND False, score True (2-of-3)
        ({"break_52w_high": True, "close_above_open": True, "close_in_top_40pct_of_range": True}, False, True),
        # Break + 1 confirmation only: score False
        ({"break_52w_high": True, "vol_spike_17x": True}, False, False),
        ({"break_52w_high": True}, False, False),
    ]
    score_fires = 0
    for sig, expected_4and, expected_score in cases:
        actual_score = _fires(sig)
        assert actual_score == expected_score, f"score-of-N mismatch on {sig}: got {actual_score}, expected {expected_score}"
        if actual_score:
            score_fires += 1
    # Score-of-N should fire more often than 4-AND (strict superset on these cases)
    and_fires = sum(1 for _, e4, _ in cases if e4)
    assert score_fires > and_fires, (
        f"score-of-N fired {score_fires}/6 cases; 4-AND would fire {and_fires}/6. "
        "Post-B697 must fire strictly more often than pre-B697."
    )
