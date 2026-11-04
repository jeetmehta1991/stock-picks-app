#!/usr/bin/env python
"""B2848 (S6-B2848a/b, owner-approved 'Approved implement' 2026-09-17): the
two mechanical gates every STEP-1 instrument runs before any grid work.

ONE definition, imported by offline_level_sweep.py and breadth_step1_grid.py
(L593: the instrument that measured a rule and the pin that holds it share
code; here the two consumers share the gate).

1. require_band_ruling: the owner's T3 band words, verbatim, REQUIRED and
   non-empty - the breadth_step2_read --ruling pattern applied to Step-1.
   Before this, a Step-1 grid could run with no owner word at all; only
   discipline stopped it (the enforcement audit the owner forced,
   2026-09-17). Its live path also runs require_valid_spec and require_current_table_a (S6-B3393).
2. require_fresh_status: the stamped status view's build.source_commit must
   equal git HEAD - the runbook §0.5 driver loop's regenerate-first precondition made mechanical.
   FAIL CLOSED on a missing or unreadable stamp (L642: the absent case is
   the case the guard exists for). `head` is injectable for tests only.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUS_JSON = ROOT / "output_audit" / "strategy_optimisation_status.json"


def require_band_ruling(text, strategy=None, *, registry=None) -> str:
    if not isinstance(text, str) or not text.strip():
        raise SystemExit(
            "REFUSED: no --band-ruling. A Step-1 grid runs only after the "
            "owner's T3 band words, recorded verbatim into the artifact "
            "(S6-B2848a; the breadth_step2_read --ruling pattern).")
    # B2855 (owner-directed 2026-09-17: "Why shouldnt r1 be mandatory
    # executed before my review?"): a T3 ruling is only CONSUMABLE for a
    # REGISTERED strategy - R1 precedes the review by construction,
    # because a ruling on an unregistered strategy cannot reach a grid
    # (L754: registration checked at launch). Fail closed on the absent
    # name (L642).
    if not isinstance(strategy, str) or not strategy.strip():
        raise SystemExit(
            "REFUSED: a band ruling binds a STRATEGY - pass the "
            "instrument's --strategy to require_band_ruling (B2855).")
    live = registry is None
    if live:
        import sys as _sys
        if str(ROOT / "scripts") not in _sys.path:
            _sys.path.insert(0, str(ROOT / "scripts"))
        from producer_variant_table import SPECS, SPECS_PHASE0
        registry = set(SPECS) | set(SPECS_PHASE0)
    if strategy.strip() not in registry:
        raise SystemExit(
            f"REFUSED: {strategy.strip()!r} has no SPECS/SPECS_PHASE0 "
            "entry - R1 registration is MANDATORY before a T3 ruling is "
            "usable (B2855, owner-directed). Register the inventory "
            "first (producer_variant_table), then re-run.")
    if live:
        # S6-B3393: R1 is validity as well as registration, and a stale
        # Table A file is regenerated before a campaign reads it
        require_valid_spec(strategy.strip())
        print(require_current_table_a(strategy.strip()))
    return text.strip()


# S6-B3393 (B3139q-r192, census 638 + 994): R1 binds an OFFLINE Step 1 too -
# the strategy's Table A entry must pass validate_spec, not only exist. The
# names that failed when this was mechanized are frozen as (strategy,
# sha256[:16] of each validate_spec message) - MEASURED 46 messages over
# 9 of the 29 registered names, all SPECS_PHASE0. PHASE0 is the
# pre-registration record and is never edited, so a name leaves this set
# when a SPECS entry for it supersedes the PHASE0 one; a NEW message on any
# name refuses. Shrink-only.
STEP1_SPEC_GRANDFATHERED = frozenset({
    ('institutional_breakout_confirmation_long', '1bb62446ba7ce3a7'),
    ('institutional_breakout_confirmation_long', '9c25bcf362415bc8'),
    ('institutional_breakout_confirmation_long', 'bd41dd845681c701'),
    ('institutional_breakout_confirmation_long', 'ed3fa75eb1f102d0'),
    ('institutional_high_conviction_long', '1bb62446ba7ce3a7'),
    ('institutional_high_conviction_long', '9c25bcf362415bc8'),
    ('institutional_high_conviction_long', 'bd41dd845681c701'),
    ('institutional_high_conviction_long', 'c0977e01ddb0fe45'),
    ('institutional_high_conviction_long', 'ed3fa75eb1f102d0'),
    ('institutional_multi_quarter_persistence_long', '1bb62446ba7ce3a7'),
    ('institutional_multi_quarter_persistence_long', '9c25bcf362415bc8'),
    ('institutional_multi_quarter_persistence_long', 'bd41dd845681c701'),
    ('institutional_multi_quarter_persistence_long', 'c0977e01ddb0fe45'),
    ('institutional_multi_quarter_persistence_long', 'ed3fa75eb1f102d0'),
    ('institutional_oversold_long', '1bb62446ba7ce3a7'),
    ('institutional_oversold_long', '9c25bcf362415bc8'),
    ('institutional_oversold_long', 'bd41dd845681c701'),
    ('institutional_oversold_long', 'c0977e01ddb0fe45'),
    ('institutional_oversold_long', 'ed3fa75eb1f102d0'),
    ('institutional_persistence_oversold_long', '1bb62446ba7ce3a7'),
    ('institutional_persistence_oversold_long', '279c8e20f0e65c10'),
    ('institutional_persistence_oversold_long', '9c25bcf362415bc8'),
    ('institutional_persistence_oversold_long', 'bd41dd845681c701'),
    ('institutional_persistence_oversold_long', 'c0977e01ddb0fe45'),
    ('institutional_persistence_oversold_long', 'ed3fa75eb1f102d0'),
    ('institutional_recent_init_momentum_long', '1bb62446ba7ce3a7'),
    ('institutional_recent_init_momentum_long', '9c25bcf362415bc8'),
    ('institutional_recent_init_momentum_long', 'bd41dd845681c701'),
    ('institutional_recent_init_momentum_long', 'c0977e01ddb0fe45'),
    ('institutional_recent_init_momentum_long', 'ed3fa75eb1f102d0'),
    ('institutional_recent_init_volume_long', '1bb62446ba7ce3a7'),
    ('institutional_recent_init_volume_long', '9c25bcf362415bc8'),
    ('institutional_recent_init_volume_long', 'bd41dd845681c701'),
    ('institutional_recent_init_volume_long', 'c0977e01ddb0fe45'),
    ('institutional_recent_init_volume_long', 'ed3fa75eb1f102d0'),
    ('institutional_strong_conviction_long', '1bb62446ba7ce3a7'),
    ('institutional_strong_conviction_long', '279c8e20f0e65c10'),
    ('institutional_strong_conviction_long', '9c25bcf362415bc8'),
    ('institutional_strong_conviction_long', 'bd41dd845681c701'),
    ('institutional_strong_conviction_long', 'c0977e01ddb0fe45'),
    ('institutional_strong_conviction_long', 'ed3fa75eb1f102d0'),
    ('xs_low_beta_with_smart_money_long', '1bb62446ba7ce3a7'),
    ('xs_low_beta_with_smart_money_long', '9c25bcf362415bc8'),
    ('xs_low_beta_with_smart_money_long', 'bd41dd845681c701'),
    ('xs_low_beta_with_smart_money_long', 'c0977e01ddb0fe45'),
    ('xs_low_beta_with_smart_money_long', 'ed3fa75eb1f102d0'),
})


def require_valid_spec(strategy: str, *, specs=None) -> None:
    """The R1 validity half for an offline Step-1 instrument (S6-B3393): the
    entry the runbook R1 probe reads (SPECS first, then SPECS_PHASE0; `specs`
    is a test seam that replaces that lookup) must return no validate_spec
    message outside STEP1_SPEC_GRANDFATHERED. Fails closed on an absent entry
    (L642)."""
    import hashlib
    import sys as _sys
    if str(ROOT / "scripts") not in _sys.path:
        _sys.path.insert(0, str(ROOT / "scripts"))
    from producer_variant_table import SPECS, SPECS_PHASE0, validate_spec
    spec = (specs.get(strategy) if specs is not None
            else SPECS.get(strategy) or SPECS_PHASE0.get(strategy))
    if spec is None:
        raise SystemExit(f"REFUSED (S6-B3393): {strategy!r} has no SPECS/SPECS_PHASE0 "
                         "entry to validate (R1, B2855)")
    new = [m for m in validate_spec(spec)
           if (strategy, hashlib.sha256(m.encode("utf-8")).hexdigest()[:16])
           not in STEP1_SPEC_GRANDFATHERED]
    if new:
        raise SystemExit(
            f"REFUSED (S6-B3393, runbook R1): {strategy}'s Table A entry fails "
            f"validate_spec with {len(new)} message(s) outside the frozen set: "
            f"{new[:3]} - R1 binds an offline Step 1 too. Fix the entry (a SPECS "
            "entry supersedes the PHASE0 pre-registration) and re-run.")


def _render_one(strategy: str) -> Path:
    """build_table_a --strategy into a temp file (S6-B3232's single render)."""
    import subprocess as _sp
    import sys as _sys
    import tempfile
    out = Path(tempfile.mkdtemp(prefix="b3393_table_a_")) / f"{strategy}.md"
    r = _sp.run([_sys.executable, str(ROOT / "scripts" / "build_table_a.py"),
                 "--strategy", strategy, "--out", str(out)],
                capture_output=True, text=True, cwd=str(ROOT), timeout=1200)
    if r.returncode != 0 or not out.is_file():
        raise SystemExit(f"REFUSED (S6-B3393): the Table A render of {strategy} failed "
                         f"(exit {r.returncode}): {(r.stdout or '')[-200:]} {(r.stderr or '')[-200:]}")
    return out


def require_current_table_a(strategy: str, *, regenerate=None, render=None) -> str:
    """S6-B3393 (runbook section 3 / T2, census 772): a Table A file whose
    content is stale is regenerated before a campaign reads it. The file is
    build_table_a.table_a_file's: a lane charter is compared with a fresh
    regeneration of its lane (preflight C18's machinery and comparison - the
    build-stamp line excluded, MEASURED B3139q-r192: 37 of 37 lane files a
    lane produces match it), the newest single-strategy render with a fresh
    render. A charter left in a lane folder by an owner-closed row is a
    departed record, frozen by S6-B3303 (a), and is reported, not compared;
    a strategy with no Table A file is reported. `regenerate` / `render` are
    test seams for the two subprocess calls (each ~100 s, MEASURED). Returns
    the one-line disclosure; refuses on a stale file."""
    import sys as _sys
    if str(ROOT / "scripts") not in _sys.path:
        _sys.path.insert(0, str(ROOT / "scripts"))
    import build_table_a as _bta
    import preflight as _pf
    found = _bta.table_a_file(strategy)
    if found is None:
        return (f"table_a: {strategy} has no Table A file (no lane charter, no "
                "output_audit render) - nothing to compare (S6-B3393)")
    kind, path = found
    rel = path.relative_to(ROOT).as_posix()
    if kind.startswith("lane:"):
        sub = kind[len("lane:"):]
        stream = dict(_bta._LANE_SUBDIRS)[sub]
        try:
            rows = json.loads(STATUS_JSON.read_text(encoding="utf-8"))["rows"]
        except Exception as exc:
            raise SystemExit(f"REFUSED (S6-B3393): status view unreadable "
                             f"({type(exc).__name__}) - the lane of {rel} cannot be read")
        row_stream = next((r.get("stream") for r in rows if r.get("strategy") == strategy), None)
        if row_stream != stream:
            return (f"table_a: {rel} is a departed record (the row's stream is "
                    f"{row_stream}, the folder's {stream}) - frozen by S6-B3303 (a), "
                    "not compared (S6-B3393)")
        args = next(a for pre, a in _pf._C18_LANES if pre == f"strategy_optimisation/{sub}/")
        fresh = Path((regenerate or _pf._c18_regenerate)([args])) / sub / f"{strategy}.md"
        remedy = "python scripts/build_table_a.py " + " ".join(args)
    else:
        fresh = Path((render or _render_one)(strategy))
        remedy = f"python scripts/build_table_a.py --strategy {strategy} --out {rel}"
    if not fresh.is_file():
        raise SystemExit(f"REFUSED (S6-B3393): a fresh regeneration did not produce "
                         f"{rel} - the generator no longer writes it (fail closed)")
    if (_pf._c18_normalise(path.read_text(encoding="utf-8"))
            != _pf._c18_normalise(fresh.read_text(encoding="utf-8"))):
        raise SystemExit(
            f"REFUSED (S6-B3393, runbook T2 / census 772): {rel} is STALE - it "
            "differs from a fresh regeneration (build-stamp line aside). "
            f"Regenerate ({remedy}) and commit it before the campaign reads it.")
    return f"table_a: {rel} is current (matches a fresh regeneration; S6-B3393)"


def require_fresh_status(head: str | None = None) -> str:
    try:
        stamp = json.loads(STATUS_JSON.read_text(encoding="utf-8"))[
            "build"]["source_commit"]
    except Exception as exc:
        raise SystemExit(
            f"REFUSED: status view stamp unreadable ({type(exc).__name__}) - "
            "regenerate scripts/build_strategy_status.py first (S6-B2848b, "
            "fail closed on the absent stamp)")
    if head is None:
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, timeout=15).stdout.strip()
    if not head or stamp != head:
        raise SystemExit(
            f"REFUSED: status view stamped {stamp!r} but HEAD is {head!r} - "
            "REGENERATE FIRST (scripts/build_strategy_status.py) and commit "
            "the fresh build; runbook section 0.5 made mechanical (S6-B2848b)")
    return stamp


def require_surviving_or_unchanged(strategy: str, survival: bool) -> None:
    """S6-B3321 (B3139q-r122): the ONE fail-closed guard for an offline
    instrument that grades a strategy's R5 fires. S6-B3320 found the class:
    the depth sweep read the surviving fires, while the companion screen and
    the breadth loader read every R5 fire. When the strategy's CURRENT gate
    keeps fewer than all of its R5 fires - the status view's survives_pct
    below 1, or a side it cannot measure - the instrument must read the
    surviving fires (survival=True); otherwise it grades fires the gate now
    removes. Silent when survival is requested or the gate is unchanged;
    fails closed on an absent status row (offline_level_sweep._survival_inputs,
    L642)."""
    if survival:
        return
    from offline_level_sweep import _survival_inputs
    pct, unmeasured = _survival_inputs(strategy)
    if unmeasured or pct is None or pct < 1.0:
        raise SystemExit(
            f"REFUSED (S6-B3320/S6-B3321): {strategy}'s current gate keeps {pct} of "
            f"its R5 fires (unmeasured sides: {unmeasured or 'none'}) - grading R5 "
            "without the survival filter reads fires the gate now removes; pass "
            "--survival")


def surviving_fam(strategy: str, fam):
    """S6-B3322 (B3139q-r155): the fires of `strategy` its CURRENT gate keeps -
    build_table_a.surviving_fires on the status view's inputs, the ONE T1
    definition the R5 instruments apply (the sweep S6-B3290, the screen
    S6-B3320, the breadth loader S6-B3321, the Step-1 searches S6-B3322).
    `fam` holds one row per fire with ticker, entry_date, direction and
    signals_at_entry; an unmeasured side's fires are dropped, since none can
    be confirmed a survivor. Refuses when no fire survives (fail closed)."""
    import build_table_a as _bta
    from offline_level_sweep import _survival_inputs
    pct, unmeasured = _survival_inputs(strategy)
    kept, _sigs, _filtered = _bta.surviving_fires(strategy, fam, pct, unmeasured)
    if kept.empty:
        raise SystemExit(
            f"REFUSED (S6-B3322): no R5 fire of {strategy} survives its current "
            f"gate (survives {pct}, unmeasured sides: {unmeasured or 'none'}) - "
            "grade an engine cube, which holds the gate its run used")
    return kept
