"""scripts/cost_projection.py (B1339, Council 365/366 owner-approved) -- the
per-batch measure-and-project cost model Fable's B1334 item 5 asked for.

Problem it solves: "$12-16 full T1a" was extrapolated LINEARLY from 10-ticker
smokes where fixed boot/SMC-install/prefetch overhead dominates and screening
parallelizes across 64 vCPUs (sublinear). That estimate is unreliable and
could blow the $50 CAD HARD cap. This fits fixed + marginal from ACTUAL
measured batches and refuses to project past the cap.

Model: wall_minutes(n) = FIXED + MARGINAL_PER_TICKER * n
  - FIXED   = boot + code-tar dl + SMC pip-install + prefetch + the 1002-day
              per-day overhead that does not scale with ticker count.
  - MARGINAL= per-ticker screening cost (sublinear >64 tickers as vCPUs
              saturate; we fit LINEAR as a CONSERVATIVE upper bound below
              saturation and flag when n exceeds vcpu_saturation).
  - >=2 measured points needed to fit both; with 1 point we can only bound
    (report FIXED-unknown, refuse a point estimate -- honest per L211).

cost = wall_minutes/60 * hourly_rate.

Budget guard: cumulative_spent + projected_next > cap => HARD STOP (exit 3).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HOURLY_RATE_USD = 1.20   # c6a.16xlarge us-east-1 spot, conservative upper
BUDGET_CAP_USD = 50.0    # owner HARD cap (CAD; treated 1:1 conservatively)
VCPU_SATURATION = 64     # c6a.16xlarge vCPUs; >this, screening is bounded


def fit(points: list[tuple[int, float]]) -> dict:
    """points = [(n_tickers, wall_minutes), ...]. Returns fixed+marginal or,
    with a single point, a bounded/unfittable result (honest)."""
    pts = sorted(set(points))
    if len(pts) < 2:
        return {"fittable": False, "n_points": len(pts),
                "note": "1 data point: FIXED vs MARGINAL not separable -- "
                        "measure batch 2 before projecting (L211)."}
    # least-squares line through the measured points
    n = len(pts)
    sx = sum(p[0] for p in pts); sy = sum(p[1] for p in pts)
    sxx = sum(p[0]**2 for p in pts); sxy = sum(p[0]*p[1] for p in pts)
    denom = n*sxx - sx*sx
    if denom == 0:
        return {"fittable": False, "note": "degenerate x (all same n)"}
    marginal = (n*sxy - sx*sy) / denom
    fixed = (sy - marginal*sx) / n
    return {"fittable": True, "fixed_min": round(fixed, 2),
            "marginal_min_per_ticker": round(marginal, 4), "n_points": n}


def project(model: dict, n: int) -> dict | None:
    if not model.get("fittable"):
        return None
    wall = model["fixed_min"] + model["marginal_min_per_ticker"] * n
    cost = wall/60 * HOURLY_RATE_USD
    return {"n_tickers": n, "wall_min": round(wall, 1),
            "cost_usd": round(cost, 2),
            "vcpu_saturated": n > VCPU_SATURATION,
            "estimate_quality": ("point" if not (n > VCPU_SATURATION)
                                 else "UPPER-BOUND (screening parallelism "
                                      "saturates >64 vCPU -> real cost lower)")}


def check_budget(spent: float, next_cost: float, cap: float = BUDGET_CAP_USD):
    projected = spent + next_cost
    ok = projected <= cap
    return ok, projected


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="output_batches/batch_ledger.json",
                    help="reads measured [(n_tickers, wall_min, cost)] + spent")
    ap.add_argument("--project", type=int, nargs="*", default=[20, 50, 100, 200, 300, 503],
                    help="ticker counts to project the ladder for")
    ap.add_argument("--next-batch-tickers", type=int, default=None,
                    help="gate the NEXT batch against the budget cap")
    args = ap.parse_args()

    led = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    points, spent = [], 0.0
    for b in led.get("batches", []):
        spent += float(b.get("cost_usd", 0) or 0)
        if b.get("wall_min") and b.get("n_tickers"):
            points.append((int(b["n_tickers"]), float(b["wall_min"])))
    model = fit(points)
    print(f"MEASURED points (n,wall_min): {points}")
    print(f"MODEL: {model}")
    print(f"SPENT so far: ${spent:.2f} / ${BUDGET_CAP_USD:.0f} cap "
          f"(${BUDGET_CAP_USD-spent:.2f} remaining)")
    if model.get("fittable"):
        print("\nLADDER PROJECTION:")
        cum = spent
        for n in args.project:
            p = project(model, n)
            cum_after = cum + p["cost_usd"]
            flag = "" if cum_after <= BUDGET_CAP_USD else "  <-- BREACHES CAP"
            print(f"  {n:4} tkr: {p['wall_min']:6.1f} min  ${p['cost_usd']:5.2f}"
                  f"  [{p['estimate_quality']}]{flag}")
    if args.next_batch_tickers is not None:
        p = project(model, args.next_batch_tickers)
        nxt = p["cost_usd"] if p else float("nan")
        ok, proj = check_budget(spent, nxt if p else 0.0)
        if not p:
            print(f"\nNEXT BATCH ({args.next_batch_tickers} tkr): cost "
                  f"UNPROJECTABLE with {model['n_points']} point(s) -- "
                  f"measure-and-project discipline: run it as the next "
                  f"measured rung, do not pre-commit a number (L211).")
            return 0
        print(f"\nNEXT BATCH ({args.next_batch_tickers} tkr): ${nxt:.2f} -> "
              f"cumulative ${proj:.2f} / ${BUDGET_CAP_USD:.0f}")
        if not ok:
            print("BUDGET_STOP: next batch would breach the HARD cap. HALT.")
            return 3
        print("BUDGET_OK.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
