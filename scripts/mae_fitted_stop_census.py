"""S6-B1248-LEVER10 (B3139q-r72x): the MAE-fitted stop census.

WHAT THE LEVER IS. The B1248 review (output_audit/COMPREHENSIVE_TRADER_REVIEW_
STRATEGIES_EXITS_2026_07_07.md, Lever 10): set each strategy's INITIAL stop
just beyond the 75th percentile of its WINNERS' maximum adverse excursion -
the move against the position a winner had to survive. This census measures
that distance per (strategy, direction) so the owner can decide whether the
stop is worth building into the engine. It simulates NO exit and grades
nothing: it reports the distribution the stop would be fitted to.

SOURCE. output_r5_merged_1_7/trade_log.parquet - one row per entry on the R5
production exit path, with the engine's max_adverse_excursion (percent of
entry, negative = adverse; exit_manager.ClosedTrade) and win. The cube file
carries only an MAE bucket per exit, so the fitted distance is a property of
the PRODUCTION exit path, recorded per row as production_exit.

WINDOW. In-sample only (entry before roster_core.HO_START): the holdout is
spent once, never on fitting.

PER (strategy, direction): trades and winners in-sample, |MAE| of winners at
p50 / p75 (percent), the stop distance the lever names (p75), the share of
in-sample LOSERS whose |MAE| reached that distance (the losers such a stop
would have ended early - a count, not a pnl), the helper's ratio-based ATR
multiplier (exit_strategies.per_strategy_mae_75th_pct_of_winners, p75 / p50
clamped to [0.5, 2.5]) and the Phase 1B roster roles (phase1b_membership, the
one reader). A pair with fewer than 20 in-sample winners is reported with
fit=None - the helper's own floor.

    python scripts/mae_fitted_stop_census.py
writes output_audit/b3139_mae_fitted_stops.json
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402
import phase1b_membership as pm  # noqa: E402
from backtest.engine.exit_strategies import per_strategy_mae_75th_pct_of_winners  # noqa: E402

LOG = ROOT / "output_r5_merged_1_7" / "trade_log.parquet"
OUT = ROOT / "output_audit" / "b3139_mae_fitted_stops.json"
MIN_WINNERS = 20


def _r(x, k=3):
    return None if x is None else round(float(x), k)


def main() -> int:
    cols = ["strategy", "direction", "entry_date", "win", "max_adverse_excursion",
            "exit_method"]
    df = pd.read_parquet(LOG, columns=cols)
    if not (df["max_adverse_excursion"] <= 0).all():
        raise SystemExit("max_adverse_excursion holds a positive value - the field no longer "
                         "means 'worst move against the position'; refusing")
    df["entry_date"] = pd.to_datetime(df["entry_date"].astype(str), errors="coerce")
    is_df = df[df["entry_date"] < pd.Timestamp(rc.HO_START)].copy()
    mem = pm.members(root=ROOT)
    rows = []
    for (s, d), g in is_df.groupby(["strategy", "direction"]):
        w = g[g["win"] == True]  # noqa: E712 - a bool column
        lo = g[g["win"] == False]  # noqa: E712
        mae_w = w["max_adverse_excursion"].abs().dropna()
        rec = {"strategy": s, "direction": d, "n_is": int(len(g)),
               "n_winners_is": int(len(w)),
               "production_exit": g["exit_method"].mode().iloc[0] if len(g) else None,
               "production_exit_share": _r(g["exit_method"].value_counts(normalize=True)
                                           .iloc[0]) if len(g) else None,
               "roster_roles": sorted(mem.get(s, {}).get("roles", [])) if s in mem else []}
        if len(mae_w) < MIN_WINNERS:
            rec.update(fit=None, reason=f"fewer than {MIN_WINNERS} in-sample winners")
        else:
            p50, p75 = float(mae_w.quantile(0.50)), float(mae_w.quantile(0.75))
            mult = per_strategy_mae_75th_pct_of_winners(g, s, direction=d)
            rec.update(fit=True, winners_mae_abs_p50_pct=_r(p50), winners_mae_abs_p75_pct=_r(p75),
                       stop_distance_pct=_r(p75),
                       losers_reaching_stop_share=_r((lo["max_adverse_excursion"].abs() >= p75)
                                                     .mean()) if len(lo) else None,
                       helper_atr_mult=mult,
                       helper_clamped=bool(mult in (0.5, 2.5)))
        rows.append(rec)
    fitted = [r for r in rows if r.get("fit")]
    roster_fitted = [r for r in fitted if r["roster_roles"]]
    out = {
        "artifact": "S6-B1248-LEVER10 MAE-fitted stop census (B3139q-r72x)",
        "source": str(LOG.relative_to(ROOT).as_posix()),
        "window": f"in-sample, entry before {rc.HO_START}",
        "descriptive_only": True,
        "pairs": len(rows), "pairs_fitted": len(fitted),
        "pairs_unfit_lt_min_winners": len(rows) - len(fitted),
        "roster_pairs_fitted": len(roster_fitted),
        # roster members with no R5 row (registered after R5) - named, never
        # dropped silently from a population (#279)
        "roster_members_absent_from_log": sorted(n for n in mem
                                                 if n not in set(df["strategy"])),
        "stop_distance_pct_quartiles_over_fitted": (
            [_r(q) for q in pd.Series([r["stop_distance_pct"] for r in fitted])
             .quantile([0.25, 0.5, 0.75])] if fitted else None),
        "helper_clamped_pairs": sum(1 for r in fitted if r["helper_clamped"]),
        "rows": sorted(rows, key=lambda r: (not r["roster_roles"], r["strategy"], r["direction"])),
    }
    OUT.write_bytes((json.dumps(out, indent=1) + "\n").encode("utf-8"))
    print(f"pairs {out['pairs']} | fitted {out['pairs_fitted']} | roster pairs fitted "
          f"{out['roster_pairs_fitted']} | stop-distance quartiles "
          f"{out['stop_distance_pct_quartiles_over_fitted']} | helper clamped "
          f"{out['helper_clamped_pairs']} | wrote {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
