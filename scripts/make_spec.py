#!/usr/bin/env python
"""S6-B3120a: campaign specs are GENERATED, never typed (the L788 remedy
applied to the WHOLE spec).

# Source: the b3119 spec shape (output_audit/b3119_*_spec.json exemplars) +
# STRATEGY_OPTIMISATION_PLAN.md phase table via phase_table.resolve; per
# CHECKLIST #77.

WHY. The B3120 audit's central diagnosis (L788, unanimous council): the
gates validate the artifact the agent authored, and the deviation is typed
INTO that artifact with a rationale - the owner's question had 7-of-7
detection, the authored gates 0-of-7. phase_table (B2713) deleted the
window/universe degrees of freedom; this deletes the REST of the spec's
typing surface. The only typed inputs are the strategy, the swept
parameter id, its levels, and the wave prefix - everything else derives
from the SPECS registry, the runbook's phase table, and the status
artifact, then the draft is validated through the CONSUMER'S OWN GATE
(producer_variant_table.launch_refusals) before it is written, so a spec
this tool emits cannot be one the launcher would refuse.

REFUSALS (fail-closed, each with its reason):
  - strategy not in SPECS (no adapter -> the battery would fail at landing);
  - parameter id not in the entry, or carrying no env actuator;
  - a level outside resim_band + {production} (off-band);
  - no positive fires_at_production in the status artifact (prelaunch_gate
    refuses a manifest without one - B2849 - so generation refuses first);
  - launch_refusals non-empty on the built draft (printed verbatim).

STEP 2 (S6-B3154a): a --step 2 spec is SIZED, not defaulted - max_legs from
the config's own Step-1 engine elapsed x the family's largest measured
Step-2/Step-1 ratio x STEP2_LEG_MARGIN, preregistered_exit from that Step-1
grid's step1_ranking[0], and the fires basis stamped with its grain. Refused
when the config has no COMPLETE Step-1 cube, its grid has no ranking, or no
Step-2 ratio has been measured anywhere. A Step-1 spec is unchanged.

Usage:
  python scripts/make_spec.py --strategy bollinger_lower --param P4 \
      --levels 50 --wave-prefix bl_demo [--step 1] [--dry] \
      [--with P6=40 ...]
One spec per level: output_audit/<wave-prefix>_<tag>_spec.json.

--with PARAM=LEVEL (S6-B3141a, opt-in, repeatable): pins a COMPANION knob of
the same entry in every arm - its env actuator and its tools.keys arm key -
so a family whose battery reads the FULL knob vector from the manifest (the
pairs adapter declares two keys; params_from_manifest fails closed on a
missing one) gets a launchable factorial cell. Same refusals as --param:
the companion must carry an env actuator and the level must sit in its
resim_band + production. A companion not named here is no longer left
out: the AUTO-PIN below writes it at production.

AUTO-PIN (S6-B3171b, L788 - the degree of freedom deleted): every knob
the family's battery reads (SPECS tools.keys) that is neither swept nor
given by --with is written at its PRODUCTION level, env actuator and arm
key, through the --with path exactly - run_postconfig.params_from_manifest
fails CLOSED at landing on a manifest missing any of them. MEASURED
(S6-B3171, 2026-10-16): the b3171 chain's configs 1 and 2 named one of
four naked-POC knobs, launch_refusals was clean on both, and each
landing's battery failed closed after the engine had run. A production
pin leaves the config's identity unchanged (_env_key drops it) and stays
out of the tag; the arm note names every auto-pinned knob. The consumer's
gate now also applies the battery's rule (launch_refusals, S6-B3171b),
so a hand-written spec missing a knob is refused before the engine runs.

--dry (S6-B3184): a dry run writes nothing, so the subset file the real
run would create may not exist yet; the draft is judged with
subset_override set to the strategy the real run writes, so a dry run is
never refused for a file it did not write.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

STATUS = ROOT / "output_audit" / "strategy_optimisation_status.json"


def refuse(msg: str) -> "int":
    print(f"REFUSED (make_spec, S6-B3120a): {msg}")
    return 2


def fires_at_production(strategy: str):
    """The family's production-gate fire projection, from the status
    artifact - stamped with its basis, refused when absent or non-positive
    (the L642 shape: the absent case is the case the guard exists for)."""
    if not STATUS.exists():
        return None, f"{STATUS.name} missing - regenerate the status artifact"
    try:
        doc = json.loads(STATUS.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"{STATUS.name} unreadable: {exc!r}"
    # schema opened, not guessed (#230a): the artifact's population lives
    # under "rows", each {strategy, projected_step1_fires, ...}
    row = None
    for s in doc.get("rows", []):
        if s.get("strategy") == strategy:
            row = s
            break
    fires = (row or {}).get("projected_step1_fires")
    if not fires or fires <= 0:
        return None, (f"no positive projected_step1_fires for {strategy} in "
                      f"{STATUS.name} - prelaunch_gate refuses a manifest "
                      "without one (B2849)")
    build = doc.get("build") or {}
    basis = (f"{STATUS.name} (build {build.get('source_commit', '?')}): "
             f"projected_step1_fires {fires} for {strategy} - the "
             "production-gate expectation per S6-B2848c; a knob swap "
             "changes the fire set both ways by construction (L812)")
    return int(round(float(fires))), basis


def _env_value(level) -> str:
    """The env-string encoding of a level - ONE definition, shared by the
    arm env (_arm_env) and config identity (_env_key, S6-B3154a), so the
    two cannot drift. S6-B3161: written in the ENGINE's parse convention
    (backtest/config.py). str(level) wrote None as 'None' and a bool as
    'True'/'False'; the None-able knobs parse `float(raw) if raw else None`
    or `int(raw) if raw else None`, so 'None' raised at config import, and
    SMC_OB_CLOSE_MITIGATION is on only for '1', so a swept True ran as
    False. None -> '' (the unset form - the b2944 candle specs ran with it)
    and a bool -> '1' / '0'. Pinned by
    test_b3161_every_spec_level_round_trips_through_the_engine_parser."""
    if level is None:
        return ""
    if isinstance(level, bool):
        return "1" if level else "0"
    return str(level)


def _arm_env(env: str, level) -> dict:
    """The arm's full env: the actuator plus any COMPANION the producer
    needs to emit the swept level. B3139 (found launching Step-2 config 2):
    STRAT_EMA_SPAN=N re-points the GATE while compute_ema_sma emits only the
    spans in EMA_PAIRS (config default '9:21,20:50,50:200,100:150' ->
    {9,20,21,50,100,150,200}); a swept span outside that set fires on keys
    the producer never writes - a zero-fire engine run. The SPECS P3/P4
    derivation and the LANDED Step-1 span-250 spec both carry the remedy:
    extend EMA_PAIRS with the production-200 pairing (the b3119 precedent's
    '200:250' form). Keyed on the ACTUATOR, shared by every EMA-gated
    strategy - never on a strategy name."""
    out = {env: _env_value(level)}
    if env == "STRAT_EMA_SPAN":
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from backtest.config import EMA_PAIRS
        emitted = {s for pair in EMA_PAIRS for s in pair}
        lev = int(level)
        if lev not in emitted:
            pair = f"200:{lev}" if lev > 200 else f"{lev}:200"
            default = ",".join(f"{f}:{s}" for f, s in EMA_PAIRS)
            out["EMA_PAIRS"] = f"{default},{pair}"
    return out


def _preleg_exemptions(step: int) -> dict:
    """B3139 (found when the bl_step2_p4_250 chain HALTed): the pre-leg bar
    audit's documented LIFECYCLE exemptions (S6-B3092b) are DATA keyed by the
    step's universe (output_audit/preleg_lifecycle_exemptions.json, tracked);
    config 1's hand-built spec carried them and this generator did not, so
    the same two documented tickers (FISV rename, SBNY failure) refused the
    next launch. The universe is DERIVED from phase_table.resolve - never
    typed (B2713). Empty when the registry has no block for the universe."""
    import json as _json
    import phase_table
    tf = Path(str(phase_table.resolve(step)["tickers_file"])).name
    reg = ROOT / "output_audit" / "preleg_lifecycle_exemptions.json"
    if not reg.is_file():
        return {}
    doc = _json.loads(reg.read_text(encoding="utf-8"))
    return dict(doc.get(tf) or {})


# ---------------------------------------------------------------------------
# S6-B3154a: a Step-2 spec is SIZED from the config's own Step-1 run.
# ---------------------------------------------------------------------------
# The generator hardcoded max_legs 3 (13.5 h at 4.5 h legs) while every
# measured Step-2 run needed 5-6 legs, wrote no preregistered_exit, and
# stamped fires_at_production with no grain - so each Step-2 launch finished
# its spec by hand (B3131 3 -> 6; B3154 3 -> 8 + preregistered_exit), the
# typing surface L788 exists to delete. Spare legs are never run (run_wave's
# leg loop breaks once the cube exists); under-sizing ends INCOMPLETE_MAX_LEGS
# and needs a resume relaunch, so the projection uses the LARGEST measured
# ratio.
# CHOSEN, not measured: 1.5. Criterion - capacity must EXCEED the projection
# (runbook section 4.9 Step 2.2); the two hand-sized precedents ran 1.39x
# (bl span 9: 27 h over 19.4 h, bl_step2_p4_9_spec.json; pairs config 2:
# 36.0 h over 22.90 h, pairs_mrl_step2_p5_0p01_p6_60_spec.json), and per-leg
# rates inside one run varied up to 1.79x (pairs production leg 1 73.93
# s/sim-day vs leg 2 132.24, output_audit/b3142r_chain_detached.log B2127
# rate lines).
STEP2_LEG_MARGIN = 1.5


def _subset_strategy(root: Path, spec: dict):
    """The ONE strategy a spec's strategy_subset file names, or None."""
    p = root / str(spec.get("strategy_subset") or "")
    try:
        names = [x.strip() for x in p.read_text(encoding="utf-8").splitlines()
                 if x.strip()]
    except OSError:
        return None
    return names[0] if len(names) == 1 else None


def _production_env(strategy: str) -> dict:
    """{env actuator: production level} for a SPECS family; {} for a
    strategy with no SPECS entry. Basis (S6-B3154a probe over the 17 SPECS
    actuators): an unset knob reads its os.environ.get default - in
    backtest/config.py for 14, and at precompute build time in
    build_institutional_persistence_precompute.py for the 3 INST_* knobs.
    10 of the 14 engine defaults equal the production level as _env_value
    writes it; the other 4 are the None/False knobs, whose encoding
    S6-B3161 aligns with the engine's parse."""
    from producer_variant_table import SPECS
    entry = SPECS.get(strategy) or {}
    return {p["env"]: p.get("production") for p in entry.get("params", [])
            if p.get("env")}


def _env_key(env: dict, production: dict | None = None) -> tuple:
    """A config's identity: its env with every knob AT its production
    level dropped (in _env_value's encoding), so {} and {K: production}
    are ONE config - the engine reads an unset knob as production."""
    prod = {str(k): _env_value(v) for k, v in (production or {}).items()}
    return tuple(sorted((str(k), str(v)) for k, v in (env or {}).items()
                        if prod.get(str(k)) != str(v)))


def _spec_step(spec: dict) -> int:
    """A spec's step: the declared `step`, else run_wave's own reading of
    step1_cube (default True -> Step 1)."""
    if str(spec.get("step")) in ("1", "2"):
        return int(spec["step"])
    return 1 if spec.get("step1_cube", True) else 2


def _complete_hours(cube: Path):
    """Engine wall hours of a COMPLETE single run (engine_state status
    'complete' + run_heartbeat elapsed_hours > 0), else None - a killed run's
    partial hours would under-size the projection."""
    try:
        st = json.loads((cube / "engine_state.json").read_text(encoding="utf-8"))
        hb = json.loads((cube / "run_heartbeat.json").read_text(encoding="utf-8"))
        h = float(hb.get("elapsed_hours"))
        done = st.get("status") == "complete"
    except (OSError, ValueError, TypeError, AttributeError):
        return None
    return h if done and h > 0 else None


def step1_siblings(root: Path, strategy: str, env: dict,
                   production: dict | None = None) -> list:
    """Every COMPLETE Step-1 cube of THIS config: a Step-1 spec under
    output_audit/ naming the same strategy whose arm carries the same env,
    compared by _env_key (a knob AT production matches the knob unset;
    `production` defaults to the strategy's SPECS levels); its cube is
    output_<wave>_<tag>."""
    if production is None:
        production = _production_env(strategy)
    want, out = _env_key(env, production), []
    for f in sorted((root / "output_audit").glob("*_spec.json")):
        try:
            spec = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (not isinstance(spec, dict) or _spec_step(spec) != 1
                or _subset_strategy(root, spec) != strategy):
            continue
        for arm in spec.get("arms") or []:
            if _env_key(arm.get("env"), production) != want:
                continue
            cube = root / f"output_{spec.get('wave')}_{arm.get('tag')}"
            h = _complete_hours(cube)
            if h is not None:
                out.append({"cube": cube.name, "hours": h, "spec": f.name,
                            "mtime": (cube / "run_heartbeat.json").stat().st_mtime})
    return out


def measured_ratios(root: Path) -> list:
    """Step-2 wall hours / the config's own Step-1 hours, for every COMPLETE
    Step-2 wave summary (not a `supersedes` resume - its elapsed covers only
    the resumed legs) whose config has a Step-1 sibling. A STALE summary is
    never read: run_wave.archive_stale_summary renames it
    <wave>_wave_summary_STALE_<ts>.json, which this glob's suffix excludes."""
    rows = []
    for f in sorted((root / "output_audit").glob("*_wave_summary.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        spec = d.get("spec") if isinstance(d, dict) else None
        if (not isinstance(spec, dict) or d.get("supersedes")
                or _spec_step(spec) != 2):
            continue
        strat = _subset_strategy(root, spec)
        if not strat:
            continue
        arms = {x.get("tag"): x for x in spec.get("arms") or []}
        for r in d.get("results") or []:
            if r.get("status") != "COMPLETE" or not r.get("elapsed_s"):
                continue
            arm = arms.get(r.get("arm"))
            sibs = step1_siblings(root, strat, (arm or {}).get("env")) if arm else []
            if not sibs:
                continue
            s1 = max(sibs, key=lambda s: s["mtime"])
            h2 = float(r["elapsed_s"]) / 3600
            rows.append({"strategy": strat, "summary": f.name, "arm": r.get("arm"),
                         "step2_hours": round(h2, 3), "step1_cube": s1["cube"],
                         "step1_hours": s1["hours"],
                         "ratio": round(h2 / s1["hours"], 3)})
    return rows


def step2_sizing(root: Path, strategy: str, env: dict, leg_cap_hours: float):
    """(sizing, None) or (None, refusal reason) for a Step-2 spec of the
    config `env`. sizing = max_legs, _capacity_note, preregistered_exit,
    preregistered_note. The Step-1 sibling chosen when several exist is the
    LATEST (a re-run of a config supersedes the earlier run)."""
    import math
    sibs = step1_siblings(root, strategy, env)
    if not sibs:
        return None, (f"no COMPLETE Step-1 cube of this config ({strategy}, env "
                      f"{dict(env)}) - Step 2 follows the config's own Step 1, "
                      "which supplies both the sizing and the preregistered exit")
    s1 = max(sibs, key=lambda s: s["mtime"])
    grid = root / "output_audit" / f"{s1['cube']}_grid_auto.json"
    try:
        rank0 = (json.loads(grid.read_text(encoding="utf-8")).get("step1_ranking")
                 or [None])[0]
    except (OSError, ValueError):
        rank0 = None
    if not isinstance(rank0, dict) or not rank0.get("exit"):
        return None, (f"{grid.name} carries no step1_ranking - the preregistered "
                      "exit (B2612) is the Step-1 rank-1 exit, so it cannot be "
                      "derived")
    rows = measured_ratios(root)
    fam = [r for r in rows if r["strategy"] == strategy]
    pool, scope = (fam, "this family's") if fam else (rows, "CROSS-FAMILY (this "
                                                     "family has no completed Step-2 run)")
    if not pool:
        return None, ("no completed Step-2 run with a Step-1 sibling exists "
                      "anywhere - the Step-2/Step-1 ratio is UNMEASURED, and "
                      "sizing from a guess is what this generator replaces")
    top = max(pool, key=lambda r: r["ratio"])
    proj = s1["hours"] * top["ratio"]
    legs = max(1, math.ceil(proj * STEP2_LEG_MARGIN / leg_cap_hours))
    note = (f"GENERATED (S6-B3154a): projection {proj:.2f} h = this config's own "
            f"Step-1 engine elapsed {s1['hours']} h ({s1['cube']}/run_heartbeat."
            f"json) x {scope} largest measured Step-2/Step-1 ratio "
            f"{top['ratio']} ({top['summary']}: {top['step2_hours']} h over "
            f"{top['step1_cube']} {top['step1_hours']} h; {len(pool)} measured). "
            f"max_legs = ceil({proj:.2f} x {STEP2_LEG_MARGIN} / {leg_cap_hours}) = "
            f"{legs}; capacity {legs * leg_cap_hours:.1f} h. Spare legs are "
            "never run - run_wave's leg loop breaks once the cube exists.")
    pre_note = (f"B2612 contract: this config's Step-1 rank-1 exit, read from "
                f"output_audit/{grid.name} step1_ranking[0] (is_ci_lo "
                f"{rank0.get('is_ci_lo')}, is_sharpe {rank0.get('is_sharpe')}). "
                "Recorded beside the grader's IS selection - never a selector; "
                "one holdout read. GENERATED (S6-B3154a).")
    return {"max_legs": legs, "_capacity_note": note,
            "preregistered_exit": rank0["exit"],
            "preregistered_note": pre_note}, None


def fires_grain(step: int) -> str:
    """The grain a fire projection was measured at vs the grain this spec runs
    at, from phase_table (never typed)."""
    import phase_table
    s1, sp = phase_table.resolve(1), phase_table.resolve(step)
    w1, wp = s1["window"], sp["window"]
    return (f"GRAIN: measured at Step-1 grain ({s1['universe_n']} tickers, "
            f"{w1['start']}..{w1['end']}); this spec runs Step {step} "
            f"({sp['universe_n']} tickers, {wp['start']}..{wp['end']}). The "
            "field gates only > 0 (prelaunch_gate, B2849) - it is not a "
            f"Step-{step} fire count (S6-B3154a).")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--param", required=True, help="SPECS param id, e.g. P4")
    ap.add_argument("--levels", required=True,
                    help="comma-separated resim levels, e.g. 9,20,50")
    ap.add_argument("--wave-prefix", required=True)
    ap.add_argument("--step", type=int, default=1, choices=(1, 2))
    # S6-B3206 (owner ruling 2026-10-18): a Step-1 spec DECLARES its
    # depth null - a repo-relative artifact path, or "none: <reason>"
    # (cross-checked by the launch gate); the override is the owner's
    # words + date, never a bare flag (the B2731 shape)
    ap.add_argument("--depth-null", default=None,
                    help="Step 1: the offline depth-null artifact "
                         "this chain answers to, or 'none: <reason>'")
    ap.add_argument("--override-depth-null", default=None,
                    help="Step 1: the OWNER's words + date lifting a "
                         "depth null priced as noise (S6-B3206)")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--with", dest="with_", action="append", default=[],
                    metavar="PARAM=LEVEL",
                    help="pin a companion knob of the same entry "
                         "(S6-B3141a; repeatable)")
    a = ap.parse_args()

    from producer_variant_table import SPECS, launch_refusals
    spec_entry = SPECS.get(a.strategy)
    if spec_entry is None:
        return refuse(f"{a.strategy!r} has no SPECS entry - register the "
                      "family (R1) before generating engine specs")
    p = next((x for x in spec_entry["params"] if x["id"] == a.param), None)
    if p is None:
        return refuse(f"{a.strategy} has no param {a.param!r}; ids: "
                      f"{[x['id'] for x in spec_entry['params']]}")
    env = p.get("env")
    if not env:
        return refuse(f"{a.strategy}.{a.param} has NO env actuator - an "
                      "engine spec cannot sweep it (S6-B2569a); wire the "
                      "actuator first")
    allowed = list(p.get("resim_band") or []) + [p.get("production")]
    knob_name = ((spec_entry.get("tools") or {}).get("keys") or {}) \
        .get(a.param, a.param.lower())

    companions = []          # (pid, env, level, arm key)
    for item in a.with_:
        cpid, _, craw = item.partition("=")
        cp = next((x for x in spec_entry["params"] if x["id"] == cpid), None)
        if cp is None or cpid == a.param:
            return refuse(f"--with {item!r}: {cpid!r} is not a companion "
                          f"param of {a.strategy} (ids "
                          f"{[x['id'] for x in spec_entry['params']]})")
        if not cp.get("env"):
            return refuse(f"--with {item!r}: {cpid} has NO env actuator")
        clev = json.loads(craw)
        callowed = list(cp.get("resim_band") or []) + [cp.get("production")]
        if clev not in callowed:
            return refuse(f"--with {item!r}: level outside {cpid} "
                          f"resim_band+production {callowed}")
        ckey = ((spec_entry.get("tools") or {}).get("keys") or {}) \
            .get(cpid, cpid.lower())
        companions.append((cpid, cp["env"], clev, ckey))

    # S6-B3171b: every battery key neither swept nor --with'd, at PRODUCTION.
    taken = {a.param} | {c[0] for c in companions}
    auto_pins = []           # (pid, env or None, production level, arm key)
    for apid, akey in dict((spec_entry.get("tools") or {})
                           .get("keys") or {}).items():
        if apid in taken:
            continue
        ap = next((x for x in spec_entry["params"] if x["id"] == apid), None)
        if ap is None:
            return refuse(f"{a.strategy}: tools.keys names {apid!r}, which "
                          "is not a param of the entry - the registry is "
                          "inconsistent, so no complete spec can be built")
        auto_pins.append((apid, ap.get("env"), ap.get("production"), akey))

    fires, basis = fires_at_production(a.strategy)
    if fires is None:
        return refuse(basis)

    subset = ROOT / "output_audit" / f"_subset_{a.strategy}.txt"
    if not a.dry:
        subset.write_text(a.strategy + "\n", encoding="utf-8")

    written = []
    for raw in a.levels.split(","):
        raw = raw.strip()
        level = json.loads(raw) if raw not in ("None", "null") else None
        if level not in allowed:
            return refuse(f"level {level!r} outside {a.strategy}.{a.param} "
                          f"resim_band+production {allowed}")
        tag = f"{a.param.lower()}_{str(level).replace('.', 'p')}" + "".join(
            f"_{cpid.lower()}_{str(clev).replace('.', 'p')}"
            for cpid, _e, clev, _k in companions)
        arm_env = _arm_env(env, level)
        for _cpid, cenv, clev, _k in companions:
            arm_env.update(_arm_env(cenv, clev))
        for _apid, aenv, alev, _k in auto_pins:
            if aenv:
                arm_env.update(_arm_env(aenv, alev))
        spec = {
            "wave": f"{a.wave_prefix}_{tag}",
            "strategy_subset": str(subset.relative_to(ROOT)).replace(
                "\\", "/"),
            "step": a.step,
            "leg_cap_hours": 4.5,
            "max_legs": 3,
            "step1_cube": a.step == 1,
            "pool_workers": 4,
            "allow_engine_drift": False,
            "resume": True,
            "cube_riders": None,
            "preleg_exemptions": _preleg_exemptions(a.step),
            "arms": [{
                "tag": tag,
                "env": arm_env,
                knob_name: level,
                **{ck: clev for _p, _e, clev, ck in companions},
                **{ak: alev for _p, _e, alev, ak in auto_pins},
                "note": (f"GENERATED by scripts/make_spec.py (S6-B3120a: "
                         f"specs derived, never typed - L788). Sweeps "
                         f"{a.strategy}.{a.param} ({p.get('param')}) via "
                         f"{env}={level}; band authority = the SPECS entry; "
                         "window/universe injected by phase_table at launch "
                         "(B2713)."
                         + (" AUTO-PINNED AT PRODUCTION (S6-B3171b - the "
                            "battery reads every declared knob): "
                            + ", ".join(f"{p_}={l_!r}" for p_, _e, l_, _k
                                        in auto_pins) + "."
                            if auto_pins else "")),
            }],
            "fires_at_production": fires,
            "_fires_basis": basis,
            "_window_note": ("DELIBERATELY ABSENT. phase_table.resolve "
                             "injects window and universe; typing them is "
                             "refused (B2713/L788)."),
            "_generated_by": "scripts/make_spec.py (S6-B3120a)",
        }
        if a.step == 1:
            # S6-B3206: the declaration rides the spec so the launch
            # gate at run_wave judges the same claim make_spec did
            if a.depth_null:
                spec["depth_null"] = {a.strategy: a.depth_null}
            if a.override_depth_null:
                spec["owner_override_depth_null"] = {
                    a.strategy: a.override_depth_null}
        if a.step == 2:
            sizing, why = step2_sizing(ROOT, a.strategy, arm_env,
                                       float(spec["leg_cap_hours"]))
            if sizing is None:
                return refuse(f"Step-2 sizing for level {level!r}: {why}")
            spec["max_legs"] = sizing["max_legs"]
            spec["_capacity_note"] = sizing["_capacity_note"]
            spec["arms"][0]["preregistered_exit"] = sizing["preregistered_exit"]
            spec["arms"][0]["preregistered_note"] = sizing["preregistered_note"]
            spec["_fires_basis"] = f"{basis} | {fires_grain(a.step)}"
        errs = launch_refusals(spec, ROOT, subset_override=(a.strategy,))
        if errs:
            return refuse(f"the consumer's own gate refuses the draft for "
                          f"level {level!r}: {errs}")
        out = ROOT / "output_audit" / f"{spec['wave']}_spec.json"
        if not a.dry:
            out.write_text(json.dumps(spec, indent=1), encoding="utf-8")
        written.append(out.name)
        print(f"[OK] {out.name}: {env}={level} "
              f"(launch_refusals clean; fires_at_production {fires})"
              + (f"; auto-pinned at production: "
                 f"{', '.join(p_ for p_, _e, _l, _k in auto_pins)}"
                 if auto_pins else "")
              + (f"; max_legs {spec['max_legs']}, preregistered_exit "
                 f"{spec['arms'][0]['preregistered_exit']}" if a.step == 2 else ""))
    print("launch: PYTHONPATH=.:scripts python scripts/launch_detached.py "
          f"--chain --batch <bNNNN> --specs {' '.join(written)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
