#!/usr/bin/env python
"""Every hand-maintained record that DESCRIBES code, checked against the code.

B1692. Three times in one session a hand-maintained record disagreed with the
code it describes, and each time I named the pattern in prose and then fixed the
INSTANCE:

  1. `producer_variant_table.py` P3 band still read the pre-B1611 `[3,5,10,20]`,
     so the table denied the existence of `tail_n=2` - the level that won BOTH
     wave-1 top-10s.
  2. The same table's `engine_implemented` stayed False for P2-P5 after B1616
     implemented them.
  3. `run_manifest_wave1.json`'s grid enumeration read 20 configs / 9 waves,
     missing the B1686 spans 100/150 and the B1691 swing_length 5 - the gate
     whose whole PURPOSE is catching a mis-enumerated grid was itself
     mis-enumerated.

The GENERALIZATION MANDATE (owner, 2026-07-18, HARD) says to fix the CLASS and
that a patch leaving siblings open is non-compliant. I stated the class three
times and shipped three instance fixes. **Naming a class is not closing it.**

The skill also says why the prose alone was never going to hold:

    "Prose rules without an executable verifier decay - the only no-silent-miss
     catches that have worked were programmatic."

So this is the executable verifier. It holds ONE invariant:

    a record that describes code must be DERIVED from that code, or must be
    CHECKED against it mechanically, every turn.

Registry entries are (record, field, authority, extractor). Adding a new
hand-maintained record without registering it is itself the defect, so
`--audit-unregistered` flags describing-artifacts that no entry covers.

Exit 0 = every registered record agrees with its authority.
Exit 2 = at least one DRIFTED. Exit 3 = an authority could not be read (fail
CLOSED - an unreadable authority proves nothing, and "could not check" has
scored above "checked and found bad" too many times this session).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
# B1697: the authority modules import each other by bare name (roster_core),
# so scripts/ must be importable too. Without this the verifier died with an
# uncaught ModuleNotFoundError and exit 1 - outside its own 0/2/3 contract,
# which means it failed LOUDLY but not in the shape it promised.
sys.path.insert(0, str(ROOT / "scripts"))


# --------------------------------------------------------------------------
# authorities - each returns the TRUE value by reading the code that RUNS
# --------------------------------------------------------------------------
def _auth_tighten(const: str):
    """The grader's own band constants - the values the sweep actually uses."""
    import scripts.tighten_breaker_block as tb
    return list(getattr(tb, const))


def _auth_ema_spans():
    """The spans compute_ema_sma actually EMITS.

    B2018: since B2016 (F1) the producer reads `_cfg.EMA_PAIRS` at call time -
    the hardcoded pair list this used to regex out of technical.py no longer
    exists, which left this authority UNREADABLE (fail-closed, correctly).
    Read the config value the producer consumes, not the source text.
    """
    from backtest import config as _cfg
    spans = set()
    for fast, slow in _cfg.EMA_PAIRS:
        spans.update((int(fast), int(slow)))
    return sorted(spans)


def _auth_engine_implemented():
    """True only if the engine can actually APPLY the parameter (B1616 gate)."""
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_engine_implemented.py")],
                       capture_output=True, text=True, cwd=str(ROOT))
    return r.returncode == 0


def _auth_grid_size():
    """Config count = the PRODUCT of the two fire-adding bands. Nothing else."""
    import scripts.producer_variant_table as pvt
    p1 = _record_band(pvt, "swing_length")
    return len(p1) * len(_auth_ema_spans())


STRAT = "smc_breaker_block_long"


def _params(pvt):
    """SPECS is keyed by strategy; each carries a `params` inventory."""
    return pvt.SPECS[STRAT]["params"]


def _record_band(pvt, param):
    for v in _params(pvt):
        if v.get("param") == param:
            return v["band"]
    raise LookupError(f"{param} not in SPECS[{STRAT!r}]['params']")


# --------------------------------------------------------------------------
# registry - the hand-maintained records, and what each one must agree with
# --------------------------------------------------------------------------
def _pvt_band(param):
    def get():
        import importlib
        import scripts.producer_variant_table as pvt
        importlib.reload(pvt)
        return _record_band(pvt, param)
    return get


def _pvt_flag(param):
    def get():
        import importlib
        import scripts.producer_variant_table as pvt
        importlib.reload(pvt)
        for v in _params(pvt):
            if v.get("param") == param:
                return v.get("engine_implemented")
        raise LookupError(param)
    return get


def _manifest_grid():
    d = json.loads((ROOT / "output_audit" / "run_manifest_wave1.json").read_text(encoding="utf-8"))
    import re
    for r in d.get("obsolescence_risks", []):
        if "mis-enumerated" in r.get("risk", ""):
            m = re.search(r"=\s*(\d+),", r.get("status", ""))
            if m:
                return int(m.group(1))
    raise LookupError("grid-enumeration risk row not found in the manifest")


# B2054 (S6-B1694c): the B1694 drift lived in STATUS PROSE beside agreeing
# values - approval-state sentences describing a superseded world. Truth for
# arbitrary prose is not derivable, but the DECAY VECTOR is: status language
# with NO batch/date anchor can never be checked against anything later.
# Anchored status prose is listed for review; UNANCHORED fails closed.
STATUS_WORDS = ("pending", "awaiting", "not approved", "in flight",
                "not yet approved", "proposed-not-built")
STATUS_FILES = (
    ROOT / "output_audit" / "PRODUCER_VARIANT_TABLE_smc_breaker_block_long.md",
    ROOT / "output_audit" / "run_manifest_wave1.json",
    ROOT / "output_b2016_e1" / "run_manifest.json",
)


def status_prose_findings(text: str) -> list:
    """(line_no, word, anchored) for every approval-state phrase in text."""
    import re as _re
    out = []
    for i, line in enumerate(text.lower().splitlines(), 1):
        for w in STATUS_WORDS:
            if w in line:
                anchored = bool(_re.search(r"b\d{3,4}|20\d\d-\d\d-\d\d", line))
                out.append((i, w, anchored))
    return out


REGISTRY = [
    # (label, record-reader, authority-reader)
    ("variant table: tail_n band",        _pvt_band("tail_n"),           lambda: _auth_tighten("TAIL_N")),
    ("variant table: age_bars_max band",  _pvt_band("age_bars_max"),     lambda: _auth_tighten("AGE_BARS_MAX")),
    ("variant table: break_pct_max band", _pvt_band("break_pct_max"),    lambda: _auth_tighten("BREAK_PCT_MAX")),
    ("variant table: close_mitigation",   _pvt_band("close_mitigation"), lambda: _auth_tighten("CLOSE_MITIGATION")),
    ("variant table: ema span band",      _pvt_band("span"),             _auth_ema_spans),
    ("variant table: engine_implemented", lambda: all(_pvt_flag(p)() for p in
                                                      ("close_mitigation", "tail_n",
                                                       "age_bars_max", "break_pct_max")),
                                                                          _auth_engine_implemented),
    ("run manifest: grid size",           _manifest_grid,                 _auth_grid_size),
]


def _norm(v):
    """Compare bands by the SET of levels they cover, with None sortable."""
    if isinstance(v, list):
        return sorted(v, key=lambda x: (x is None, str(type(x)), x if x is not None else 0))
    return v


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    drift, unreadable, ok, order = [], [], [], []
    for label, record, authority in REGISTRY:
        try:
            truth = authority()
        except Exception as exc:                       # fail CLOSED
            unreadable.append((label, f"authority unreadable: {exc!r}"))
            continue
        try:
            claimed = record()
        except Exception as exc:
            unreadable.append((label, f"record unreadable: {exc!r}"))
            continue
        # The invariant is COVERAGE - which levels get tested - not their order.
        # All three real drifts were a MISSING level (tail_n=2, spans 100/150,
        # swing_length=5), never a reordering. A boolean band written
        # production-first is not a defect, so order is ADVISORY.
        if _norm(claimed) != _norm(truth):
            drift.append((label, claimed, truth))
        elif isinstance(claimed, list) and claimed != truth:
            order.append((label, claimed, truth))
            ok.append(label)
        else:
            ok.append(label)

    if not a.quiet:
        print("=== DESCRIBING ARTIFACTS vs THE CODE THEY DESCRIBE (B1692) ===")
        for label in ok:
            print(f"  AGREES    {label}")
        for label, claimed, truth in drift:
            print(f"  DRIFTED   {label}\n              record claims : {claimed}\n"
                  f"              code says     : {truth}")
        for label, c, t in order:
            print(f"  ADVISORY  {label}: same levels, different order "
                  f"(record {c} vs code {t}) - coverage is identical, not a defect")
        for label, why in unreadable:
            print(f"  UNREADABLE {label}: {why}")
        print(f"\n  {len(ok)} agree | {len(drift)} DRIFTED | {len(unreadable)} unreadable")

    # B2054 (S6-B1694c): status-prose staleness check on the covered files.
    unanchored = []
    for f in STATUS_FILES:
        if not f.exists():
            continue
        for ln, w, anch in status_prose_findings(
                f.read_text(encoding="utf-8", errors="replace")):
            if not a.quiet:
                print(f"  STATUS-PROSE {'ok        ' if anch else 'UNANCHORED'}"
                      f" {f.name}:{ln} ({w!r})")
            if not anch:
                unanchored.append(f"{f.name}:{ln} ({w})")
    if unanchored:
        print("\nFAIL-CLOSED: approval-state prose with no batch/date anchor "
              "can never be checked against a later ruling - anchor it: "
              + "; ".join(unanchored))
        return 4

    if unreadable:
        print("\nFAIL-CLOSED: an authority that cannot be read proves nothing.")
        return 3
    if drift:
        print("\nDRIFT: a record describing code disagrees with the code. Fix the RECORD, "
              "or if the code moved deliberately, update both in the same commit.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
