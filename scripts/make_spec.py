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
resim_band + production. Absent, the spec is byte-identical to before.
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
    out = {env: str(level)}
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--param", required=True, help="SPECS param id, e.g. P4")
    ap.add_argument("--levels", required=True,
                    help="comma-separated resim levels, e.g. 9,20,50")
    ap.add_argument("--wave-prefix", required=True)
    ap.add_argument("--step", type=int, default=1, choices=(1, 2))
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
                "note": (f"GENERATED by scripts/make_spec.py (S6-B3120a: "
                         f"specs derived, never typed - L788). Sweeps "
                         f"{a.strategy}.{a.param} ({p.get('param')}) via "
                         f"{env}={level}; band authority = the SPECS entry; "
                         "window/universe injected by phase_table at launch "
                         "(B2713)."),
            }],
            "fires_at_production": fires,
            "_fires_basis": basis,
            "_window_note": ("DELIBERATELY ABSENT. phase_table.resolve "
                             "injects window and universe; typing them is "
                             "refused (B2713/L788)."),
            "_generated_by": "scripts/make_spec.py (S6-B3120a)",
        }
        errs = launch_refusals(spec, ROOT)
        if errs:
            return refuse(f"the consumer's own gate refuses the draft for "
                          f"level {level!r}: {errs}")
        out = ROOT / "output_audit" / f"{spec['wave']}_spec.json"
        if not a.dry:
            out.write_text(json.dumps(spec, indent=1), encoding="utf-8")
        written.append(out.name)
        print(f"[OK] {out.name}: {env}={level} "
              f"(launch_refusals clean; fires_at_production {fires})")
    print("launch: PYTHONPATH=.:scripts python scripts/launch_detached.py "
          f"--chain --batch <bNNNN> --specs {' '.join(written)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
