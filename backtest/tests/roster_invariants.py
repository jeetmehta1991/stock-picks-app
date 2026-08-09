"""backtest/tests/roster_invariants.py (B1488, ticket S6-B1471d) -- DERIVE the roster's
structural counts once, so no two test files can disagree about them.

WHY THIS EXISTS
The count of dual `_strat3` strategies was asserted independently in `test_batch743` (pin3) AND
`test_batch744` (pin2). When B1465 converted `prev_day_high_break` from `_strat3` to `_strat`, I
updated the copy that failed in front of me and left the other at the old value -- invisible,
because that file sits outside the enforced gate. The same duplication explains the pure-short
population reading 50 in `test_batch741` and 51 in `test_batch744` while three roster batches
(B1010 +1, B1382 +3, B1189 -1) updated neither.

**A duplicated pin does not double protection; it halves it** -- the first copy to fail gets fixed
and the second silently records the old world (L317).

These helpers read `screener.py` and count. Tests import them and assert against a single expected
number, so a roster change moves ONE constant instead of N scattered literals, and any file that
forgets to update is impossible rather than merely unlucky.
"""
from __future__ import annotations

import re
from pathlib import Path

SCREENER = Path(__file__).resolve().parents[1] / "signals" / "screener.py"


def _src() -> str:
    return SCREENER.read_text(encoding="utf-8")


def dual_strat3_count(src: str | None = None) -> int:
    """Strategies constructed via `_strat3(...)` -- i.e. genuinely bidirectional."""
    return len(re.findall(r"return _strat3\(", src if src is not None else _src()))


def pure_short_count(src: str | None = None) -> int:
    """Strategies constructed via `_strat(<var>, "short"...)` -- standalone shorts."""
    return len(re.findall(r'_strat\([A-Za-z_]\w*,\s*"short"',
                          src if src is not None else _src()))


def pure_long_count(src: str | None = None) -> int:
    return len(re.findall(r'_strat\([A-Za-z_]\w*,\s*"long"',
                          src if src is not None else _src()))


# Single source of truth for the expected values. A roster change updates THESE and
# nothing else; every consumer imports rather than re-literals them.
#
# LINEAGE -- why each number is what it is:
#   dual 59   : 61 -> 60 at B899 (B874 deleted camarilla_rsi_obv);
#               60 -> 59 at B1465 (prev_day_high_break _strat3 -> _strat, its SHORT branch was
#               character-identical to standalone prev_day_low_breakdown)
#   short 53  : 50 + 1 (B1010 insider_cluster_concentrated_sell_short)
#               + 3 (B1382 mirror shorts) - 1 (B1189 deleted dxy_headwind_multinational_short)
EXPECTED_DUAL_STRAT3 = 59
EXPECTED_PURE_SHORT = 53
