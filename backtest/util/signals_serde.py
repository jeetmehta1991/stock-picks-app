"""backtest/util/signals_serde.py - signals_at_entry serialization contract.

# Source: per CHECKLIST #77 canonical-source; B1260 Council 303
# S6-B1250-ENG1-SIGNALS-ROUNDTRIP owner-approved 2026-07-08.

WRITER-READER CONTRACT (PIVOT #37 class; pin tests in test_unit.py
test_b1260_*): every serialization of ClosedTrade.signals_at_entry /
context_bullets MUST go through dumps_signals(); every read-back MUST go
through loads_signals().

Why this module exists (B1250 ENG-1, VERIFIED): the engine checkpoint
wrote `str(dict)` containing numpy scalar reprs (`np.float64(...)`,
`np.True_`) and bare `nan`; writer.py wrote JSON booleans (`true`/
`false`). The resume reader used `ast.literal_eval`, which parses
NEITHER -> silently defaulted to {} -> every checkpoint/resume round-trip
wiped signals_at_entry for every trade (Batch A: 255/255 sampled trades
carried 0-4 keys). Blast radius: cube-replay ATR fell back to a
2pct-of-price proxy and ALL signal-conditional exits degraded to their
fallback trails.

Design:
  dumps_signals(obj)  -> canonical JSON string (numpy -> native, nan/inf
                         -> None, date -> isoformat, set -> sorted list).
  loads_signals(s, default) -> tolerant reader, in order:
      1. json.loads             (canonical format, this module's writes)
      2. ast.literal_eval       (legacy Python-repr strings)
      3. legacy-repr rescue (regex np.float64(x)->x, np.True_->True,
         bare nan->None, datetime.date(Y, M, D)->'YYYY-MM-DD') then
         literal_eval  (pre-B1260 checkpoint files AND the B2574 raw
         kill-flush files - see below)
      4. default (+ module-level one-shot counter for observability)

B2574 (S6-B2512 CAUSE FOUND, 2026-09-03): two checkpoint writers in
backtest.py (the B2148 kill-state flush and the max-run-hours cap-kill
flush) bypassed dumps_signals() and wrote raw `str(vars(t))`. Every trade
carries `short_interest_settlement_date`, a `datetime.date`, whose repr
`datetime.date(2025, 3, 31)` is neither JSON nor a literal -> steps 1-3
all failed -> `{}` on restore. MEASURED on output_icg_span100_span100:
313 of 313 leg-1 rows restored as {} (100 pct), and the cube replay then
ran on the 2pct-of-price ATR proxy for 313/374 trades (83.7 pct,
backtest_v2.log 2026-09-02 21:13:53). The fix is two-sided: the writers
now share `backtest.engine.backtest.closed_trade_rows()` (one serialising
path), and step 3 here rescues the datetime repr so a leg written by the
OLD code still restores under the new reader (the resume subprocess loads
fresh; the in-flight leg does not).
"""
from __future__ import annotations

import ast
import json
import logging
import math
import re
from datetime import date, datetime

logger = logging.getLogger(__name__)

#: count of loads that fell through to default (read by post-run health
#: checks; a nonzero value on a fresh-format run indicates a NEW writer
#: format drifted from this contract).
LOADS_FAILED_COUNT = 0
_FAIL_LOGGED = False

_NP_SCALAR_RE = re.compile(r"np\.(?:float|int|uint)\d*\(([^)]*)\)")
_NP_BOOL_TRUE_RE = re.compile(r"np\.True_")
_NP_BOOL_FALSE_RE = re.compile(r"np\.False_")
_BARE_NAN_RE = re.compile(r"(?<![A-Za-z0-9_'\"])(nan|inf|-inf)(?![A-Za-z0-9_'\"])")
# B2574: `datetime.date(2025, 3, 31)` / `datetime.datetime(2025, 3, 31, 9, 30, 0)`
# reprs from the raw kill-flush writers -> the ISO string sanitize_for_json()
# would have written. Non-integer args (never seen) collapse to None.
_DT_REPR_RE = re.compile(r"datetime\.(?:date|datetime)\(([^)]*)\)")


def _dt_repr_to_iso(m) -> str:
    try:
        nums = [int(x.strip()) for x in m.group(1).split(",") if x.strip()]
    except ValueError:
        return "None"
    if len(nums) == 3:
        return "'%04d-%02d-%02d'" % tuple(nums)
    if len(nums) >= 6:
        return "'%04d-%02d-%02dT%02d:%02d:%02d'" % tuple(nums[:6])
    return "None"


def sanitize_for_json(obj):
    """Recursively coerce to JSON-native types. numpy scalars -> python via
    .item(); NaN/inf -> None; date/datetime -> isoformat; set -> sorted list;
    anything else unknown -> str(obj)."""
    if obj is None or isinstance(obj, (bool, int, str)):
        return obj
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if hasattr(obj, "item") and not isinstance(obj, (dict, list, tuple, set)):
        # numpy scalar (np.float64 / np.bool_ / np.int64 ...)
        try:
            return sanitize_for_json(obj.item())
        except Exception:
            return str(obj)
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    if isinstance(obj, set):
        return sorted(str(v) for v in obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return str(obj)


def dumps_signals(obj) -> str:
    """Canonical serialization for signals_at_entry / context_bullets."""
    return json.dumps(sanitize_for_json(obj))


def loads_signals(value, default):
    """Tolerant read-back. Accepts canonical JSON, legacy Python reprs,
    and pre-B1260 numpy-contaminated reprs. Falls back to `default` and
    increments LOADS_FAILED_COUNT (one-shot WARNING) when unparseable."""
    global LOADS_FAILED_COUNT, _FAIL_LOGGED
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, float):
        # NaN cell from CSV read
        return default
    s = str(value).strip()
    if not s:
        return default
    # 1. canonical JSON
    try:
        return json.loads(s)
    except (ValueError, TypeError):
        pass
    # 2. legacy Python repr
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        pass
    # 3. legacy repr rescue (pre-B1260 numpy reprs; B2574 datetime reprs
    #    written by the raw kill-flush writers)
    try:
        rescued = _NP_SCALAR_RE.sub(r"\1", s)
        rescued = _NP_BOOL_TRUE_RE.sub("True", rescued)
        rescued = _NP_BOOL_FALSE_RE.sub("False", rescued)
        rescued = _BARE_NAN_RE.sub("None", rescued)
        rescued = _DT_REPR_RE.sub(_dt_repr_to_iso, rescued)
        return ast.literal_eval(rescued)
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        pass
    # 4. default + observability
    LOADS_FAILED_COUNT += 1
    if not _FAIL_LOGGED:
        _FAIL_LOGGED = True
        logger.warning(
            "signals_serde.loads_signals: unparseable value (first occurrence; "
            "subsequent counted silently in LOADS_FAILED_COUNT): %.120s", s)
    return default


__all__ = ["sanitize_for_json", "dumps_signals", "loads_signals",
           "LOADS_FAILED_COUNT"]
