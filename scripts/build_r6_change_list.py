"""scripts/build_r6_change_list.py (B1410) -- assemble the PRE-REGISTERED R6 change list.

Owner directive 2026-07-27: "assemble the change list now from what's valid - 42 tightening +
73 loosening. Then we will work on the remaining. For the remaining we will need to do either
loosening or optimizing/tightening depending on the fire rates as earlier."

ROUTING RULE (owner, B1398) - treatment is decided by FIRE COUNT, not by preference:
    fires <  100  STARVED   -> LOOSEN  (cannot reach min_trades, so no verdict is possible)
    100-299       QUIET     -> LOOSEN  (selective)
    fires >= 300  HIGH-FIRE -> TIGHTEN (volume is fine; win rate / R:R / Sharpe is the problem)
A strategy is never proposed for both, and a high-fire strategy is never loosened.

INPUTS (all IS-window only; the holdout is never read)
  b1408_tightening_proposals.json   42 strategies with a +EV per-ticker filter. VALID - built
                                    from `signals_at_entry`, i.e. the ENGINE's own output.
  b1404_clause_admission_40t.json   loosening sweep. VALID ONLY for the 73 strategies with no
                                    ABSENT-PRODUCER clause (L248: the measurement stack emits
                                    622 signals/bar vs the engine's 835, so any strategy whose
                                    gates touch a missing signal has wrong base_rate/lift/sweep).
  b1409_loosening_validity.json     which strategies are clean.
  b1398_r6_fire_segmentation.json   fire counts -> routing.

PRE-REGISTRATION. Every row carries the EXPECTED effect before R6 runs. That is what makes R6
a TEST rather than a search: a prediction recorded in advance can be wrong, and we will be able
to say so. All numbers here are IN-SAMPLE; none of them is evidence that the change works.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_passed_strategy_exit_list import parse_roster  # noqa: E402

AUD = REPO / "output_audit"
MIN_FWD_RET = 0.0        # a loosening must admit trades with positive forward return
MIN_XSV_STRICT = 0.75    # B1408 caveat: mid-band signals are partly market-wide

# B1411 (owner: "missing guard: a maximum admission ratio - add").
# Found by working the weekly_bias_pullback_long example: every existing guard PASSED and the
# change was still wrong - it took an 18-fire strategy to ~10,754 fires. That is not loosening
# a filter, it is deleting the strategy's selectivity; whatever survives is not the strategy any
# more. Its real gate is `rsi_14 < 45` (a pullback); relaxing to `< 67.5` admits almost any bar.
MAX_ADMISSION_RATIO = 5.0     # a relaxation may at most 5x a strategy's fire count

# B1411 UNIT BUG found in the same example: `fires_is` comes from trade_log (the FULL 614-ticker
# cube) while `extra_fires` comes from the 40-ticker clause-admission run. The change list
# compared them directly, so the fire target was wrong by ~15x. Normalise before comparing.
FULL_UNIVERSE_TICKERS = 614
SWEEP_SAMPLE_TICKERS = 40
UNIVERSE_SCALE = FULL_UNIVERSE_TICKERS / SWEEP_SAMPLE_TICKERS


def load(name):
    p = AUD / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> int:
    roster = parse_roster()
    tight = load("b1414_tightening_proposals_v2.json") or load("b1408_tightening_proposals.json")
    loose = load("b1418_loosening_enginestack.json") or load("b1404_clause_admission_40t.json")
    valid = load("b1409_loosening_validity.json")
    seg = load("b1398_r6_fire_segmentation.json")
    if not all([tight, loose, valid, seg]):
        print("[ERROR] missing an input artifact")
        return 1

    fires = {s: v["fires"] for s, v in seg["by_strategy"].items()}
    never = set(seg["never_fired"])
    clean = {r["strategy"] for r in loose["results"] if not any(c["verdict"].startswith("ABSENT") for c in r["clauses"])}  # B1419: from the CURRENT run

    def segment(s):
        if s in never:
            return "NEVER"
        f = fires.get(s, 0)
        return "STARVED" if f < 100 else ("QUIET" if f < 300 else "HIGH-FIRE")

    changes, skipped = [], []

    # ---- TIGHTEN: high-fire strategies, best +EV per-ticker filter, one per strategy ----
    best = {}
    for c in tight["positive_ev_proposals"]:
        s = c["strategy"]
        if segment(s) != "HIGH-FIRE":
            skipped.append({"strategy": s, "reason": f"tightening proposed but segment={segment(s)}"
                                                     " - routing rule forbids tightening a non-high-fire strategy"})
            continue
        if c["cross_sectional_variation"] < MIN_XSV_STRICT or (c.get("between_ticker_share") or 0) > 0.50:
            skipped.append({"strategy": s, "signal": c["add_gate"],
                            "reason": f"cross-sectional variation {c['cross_sectional_variation']} "
                                      f"< {MIN_XSV_STRICT} - partly market-wide (B1408 caveat)"})
            continue
        if s not in best or c["exp_after"] > best[s]["exp_after"]:
            best[s] = c
    for s, c in best.items():
        changes.append({
            "strategy": s, "cluster": roster.get(s, {}).get("category", "?"),
            "direction": roster.get(s, {}).get("direction", "?"),
            "segment": "HIGH-FIRE", "fires_is": fires.get(s),
            "treatment": "TIGHTEN", "change": f"ADD gate: {c['add_gate']}",
            "expected": {"fires": f"{c['fires_before']} -> {c['fires_after']}",
                         "win_rate": f"{c['wr_before']:.3f} -> {c['wr_after']:.3f}",
                         "expectancy_pct": f"{c['exp_before']:+.3f} -> {c['exp_after']:+.3f}",
                         "payoff": f"{c['payoff_before']} -> {c['payoff_after']}"},
            "evidence": {"n_dates_kept": c["n_dates_kept"], "top_date_share": c["top_date_share"],
                         "cross_sectional_variation": c["cross_sectional_variation"],
                         "p_date_clustered": c["p_date_clustered"]},
            "prediction_for_r6": (f"holdout expectancy > {c['exp_before']:+.3f}% (the unfiltered "
                                  f"baseline) with >= {int(c['fires_after'] * 0.5)} fires"),
        })

    # ---- LOOSEN: starved/quiet strategies from the CLEAN subset only ----
    for r in loose["results"]:
        s = r["strategy"]
        if s not in clean:
            continue
        segn = segment(s)
        if segn not in ("STARVED", "QUIET", "NEVER"):
            continue
        cands = []
        for c in r["clauses"]:
            if not c["verdict"].startswith("BINDING") or not c.get("sweep"):
                continue
            for sw in c["sweep"]:
                if sw["extra_fires"] > 0 and (sw["mean_fwd_return_of_new_pct"] or -1) > MIN_FWD_RET:
                    cands.append((c, sw))
        if not cands:
            continue
        # B1411: normalise the 40-ticker sweep count to the full universe BEFORE comparing it
        # to a full-universe fire count, then apply the admission-ratio cap.
        cur = max(fires.get(s, 0), 1)
        scored = []
        for c, sw in cands:
            extra_full = sw["extra_fires"] * UNIVERSE_SCALE
            ratio = (cur + extra_full) / cur
            scored.append((c, sw, extra_full, ratio))
        within = [x for x in scored if x[3] <= MAX_ADMISSION_RATIO]
        if not within:
            best = min(scored, key=lambda x: x[3])
            skipped.append({"strategy": s, "clause": best[0]["clause"],
                            "reason": f"every relaxation exceeds the {MAX_ADMISSION_RATIO}x admission "
                                      f"cap - smallest is {best[3]:,.0f}x ({cur} -> "
                                      f"{cur + best[2]:,.0f} fires). Loosening cannot reach "
                                      f"min_trades without destroying the strategy's selectivity."})
            continue
        # minimum sufficient: smallest multiple that still reaches the fire target
        target = max(100 - cur, 0)
        ok = [x for x in within if x[2] >= target] or within
        c, sw, extra_full, ratio = min(ok, key=lambda x: (x[1]["multiple"], -x[2]))
        changes.append({
            "strategy": s, "cluster": roster.get(s, {}).get("category", "?"),
            "direction": roster.get(s, {}).get("direction", "?"),
            "segment": segn, "fires_is": fires.get(s, 0),
            "treatment": "LOOSEN",
            "change": f"RELAX {c['clause']} by x{sw['multiple']} -> threshold {sw['new_threshold']}",
            "expected": {"fires_now_full_universe": cur,
                         "fires_after_full_universe": round(cur + extra_full),
                         "admission_ratio": round(ratio, 2),
                         "raw_extra_fires_on_40_tickers": sw["extra_fires"],
                         "fwd_return_of_new_trades_pct": sw["mean_fwd_return_of_new_pct"],
                         "clause_lift_ceiling": c["lift"]},
            "evidence": {"verdict": c["verdict"].split(" (")[0],
                         "signal_own_rate": c.get("signal_own_rate")},
            "prediction_for_r6": (f"fires rise from {fires.get(s,0)} toward >= 100 (min_trades) "
                                 f"and expectancy does not fall below the current level"),
        })

    changes.sort(key=lambda c: (c["treatment"], c["cluster"], c["strategy"]))
    tighten = [c for c in changes if c["treatment"] == "TIGHTEN"]
    loosen = [c for c in changes if c["treatment"] == "LOOSEN"]

    # ---- remaining work, routed by the same rule ----
    all_r6 = set(json.loads((AUD / "b1396_r6_strategy_list.json").read_text())["r6_strategies"])
    covered = {c["strategy"] for c in changes}
    remaining = {}
    for s in sorted(all_r6 - covered):
        segn = segment(s)
        remaining.setdefault(("TIGHTEN" if segn == "HIGH-FIRE" else "LOOSEN") + " / " + segn, []).append(s)

    out = {
        "generated": "B1410", "status": "PRE-REGISTERED PROPOSAL - nothing applied",
        "window": "IS only 2022-05-05 -> 2025-05-05; holdout never read",
        "routing_rule": {"<100": "LOOSEN", "100-299": "LOOSEN (selective)", ">=300": "TIGHTEN"},
        "counts": {"total_changes": len(changes), "tighten": len(tighten), "loosen": len(loosen),
                   "strategies_covered": len(covered), "r6_total": len(all_r6),
                   "remaining_uncovered": len(all_r6 - covered)},
        "changes": changes, "skipped_with_reason": skipped,
        "remaining_work_routed": {k: {"n": len(v), "strategies": v} for k, v in sorted(remaining.items())},
    }
    (AUD / "b1410_r6_change_list.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    md = ["<!-- Auto-generated by scripts/build_r6_change_list.py (B1410). Do NOT hand-edit. -->\n",
          "# R6 Pre-Registered Change List\n",
          "> **NOTHING HERE IS APPLIED.** Every change below is a PREDICTION recorded before R6 "
          "runs - that is what makes R6 a test rather than a search. All evidence is IN-SAMPLE "
          "(2022-05-05 -> 2025-05-05); the holdout was never read.\n",
          "## Routing rule (owner, B1398): treatment follows FIRE COUNT, never preference\n",
          "| Segment | Fires (3y IS) | Treatment | Why |\n|---|---|---|---|\n"
          "| STARVED | < 100 | **LOOSEN** | below `min_trades`, so no verdict is possible at any edge |\n"
          "| QUIET | 100-299 | **LOOSEN** (selective) | marginal statistical power |\n"
          "| HIGH-FIRE | >= 300 | **TIGHTEN** | volume is fine; win rate / R:R / Sharpe is the problem |\n",
          f"\n## Summary: {len(changes)} changes covering {len(covered)} of {len(all_r6)} R6 strategies\n",
          f"| | n |\n|---|---|\n| TIGHTEN (add a selectivity gate) | **{len(tighten)}** |\n"
          f"| LOOSEN (relax a binding threshold) | **{len(loosen)}** |\n"
          f"| Skipped with reason | {len(skipped)} |\n"
          f"| Remaining, not yet covered | {len(all_r6) - len(covered)} |\n"]
    if tighten:
        md.append("\n## A. TIGHTEN - high-fire strategies, add a selectivity gate\n")
        md.append("| Strategy | Cluster | Fires | Add gate | Fires after | Win rate | Expectancy %/trade | Dates | XS-var |\n"
                  "|---|---|---|---|---|---|---|---|---|")
        for c in tighten:
            e, ev = c["expected"], c["evidence"]
            md.append(f"| `{c['strategy']}` | {c['cluster']} | {c['fires_is']} | `{c['change'][10:]}` | "
                      f"{e['fires']} | {e['win_rate']} | **{e['expectancy_pct']}** | "
                      f"{ev['n_dates_kept']} | {ev['cross_sectional_variation']} |")
    if loosen:
        md.append("\n## B. LOOSEN - starved/quiet strategies, relax the binding threshold\n")
        md.append("| Strategy | Cluster | Segment | Fires | Change | Fires after (admission ratio) | Fwd return of NEW trades |\n"
                  "|---|---|---|---|---|---|---|")
        for c in loosen:
            e = c["expected"]
            md.append(f"| `{c['strategy']}` | {c['cluster']} | {c['segment']} | {c['fires_is']} | "
                      f"{c['change']} | {e['fires_now_full_universe']} -> {e['fires_after_full_universe']} ({e['admission_ratio']}x) | "
                      f"{e['fwd_return_of_new_trades_pct']:+.2f}% |")
    md.append(f"\n## C. Why only {len(changes)} and not more\n")
    md.append(f"- **{sum(1 for s in skipped if 'routing rule forbids' in s['reason'])}** tightening "
              "candidates were for strategies that are NOT high-fire - the routing rule forbids "
              "tightening those; they belong in the loosening queue.\n"
              f"- **{sum(1 for s in skipped if 'cross-sectional' in s['reason'])}** were rejected for "
              "cross-sectional variation < 0.75, i.e. the signal is partly MARKET-WIDE and would "
              "select periods rather than trades (L247).\n"
              "- On the loosening side, a candidate must both relax a genuinely BINDING clause AND "
              "admit new trades with POSITIVE forward return. Most did not.\n")
    md.append(f"\n## D. Remaining work - {len(all_r6) - len(covered)} strategies, routed by the same rule\n")
    md.append("| Queue | n |\n|---|---|")
    for k, v in sorted(remaining.items()):
        md.append(f"| {k} | {len(v)} |")
    md.append("\nThe loosening queue is blocked on the measurement-stack fix (L248): the clause-admission "
              "tool emits 622 signals/bar against the engine's 835, so any strategy whose gates touch a "
              "missing signal has an unreliable base rate. 116 of 198 are affected.\n")
    (REPO / "R6_CHANGE_LIST.md").write_text("\n".join(md), encoding="utf-8")

    print(f"[CHANGE LIST] {len(changes)} pre-registered changes: "
          f"{len(tighten)} TIGHTEN + {len(loosen)} LOOSEN, covering {len(covered)}/{len(all_r6)} R6 strategies")
    print(f"  skipped with reason: {len(skipped)}")
    print(f"\n  {'strategy':<40}{'cluster':<22}{'seg':<10}{'change':<52}")
    for c in changes[:40]:
        print(f"  {c['strategy']:<40}{c['cluster']:<22}{c['segment']:<10}{c['change'][:50]:<52}")
    print(f"\n  REMAINING WORK (routed by fire rate):")
    for k, v in sorted(remaining.items()):
        print(f"    {k:<26}{len(v):>4} strategies")
    print(f"\n[OK] wrote {AUD / 'b1410_r6_change_list.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
