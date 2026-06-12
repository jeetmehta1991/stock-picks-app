# Source: B710 reviewer "fire-count ceiling" finding + B711 cluster-wide sweep + S4-B710-FIRE-COUNT-CEILING-VERDICT-LOGIC per CHECKLIST #77
"""
fire_count_ceiling_classify.py
===============================

Apply the B710 reviewer's fire-count CEILING logic to the measured B660 data.
The reviewer's framing: a strategy firing >N×/name/year is failing selectivity
and should be flagged TOO-FREQUENT, just as a strategy firing <30×/yr is
flagged FAIL_FIRE_STARVED.

Default ceiling: 5,000 fires/yr per direction (~10/name/yr at T1a~500).
TOO-FREQUENT_BORDERLINE at 0.8x ceiling (4,000/yr).
TOO-FREQUENT_FAIL above ceiling.

Usage:
    python scripts/fire_count_ceiling_classify.py \\
        --input output_audit/fire_count_measured_b660_post_b689_extended.json \\
        --ceiling-per-year-per-direction 5000 \\
        --window-years 6.41 \\
        --output output_audit/fire_count_ceiling_classification_b716.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def classify(input_path: Path, ceiling: float, window_years: float, output_path: Path) -> int:
    with open(input_path) as f:
        data = json.load(f)

    borderline = ceiling * 0.8
    classifications = []
    too_freq_fail = []
    too_freq_borderline = []
    measured_ok = []
    fire_starved = []

    for s in data.get("results", []):
        name = s["strategy"]
        long_total = s.get("n_fires_long", 0)
        short_total = s.get("n_fires_short", 0)
        long_per_yr = long_total / window_years
        short_per_yr = short_total / window_years

        # Per-direction classification
        long_class = _classify_single(long_per_yr, ceiling, borderline, threshold_min=30)
        short_class = _classify_single(short_per_yr, ceiling, borderline, threshold_min=30)

        # Overall verdict: worst of the two ACTIVE sides (dead-side direction excluded)
        verdicts = []
        if long_total > 0:
            verdicts.append(long_class)
        if short_total > 0:
            verdicts.append(short_class)
        if not verdicts:
            overall = "BOTH_ZERO"
        elif "TOO_FREQUENT_FAIL" in verdicts:
            overall = "TOO_FREQUENT_FAIL"
        elif "TOO_FREQUENT_BORDERLINE" in verdicts:
            overall = "TOO_FREQUENT_BORDERLINE"
        elif "MEASURED_OK" in verdicts:
            overall = "MEASURED_OK"
        else:
            overall = "FAIL_FIRE_STARVED"

        row = {
            "strategy": name,
            "long_total": long_total,
            "short_total": short_total,
            "long_per_year": round(long_per_yr, 1),
            "short_per_year": round(short_per_yr, 1),
            "long_class": long_class,
            "short_class": short_class,
            "overall": overall,
        }
        classifications.append(row)

        if overall == "TOO_FREQUENT_FAIL":
            too_freq_fail.append(row)
        elif overall == "TOO_FREQUENT_BORDERLINE":
            too_freq_borderline.append(row)
        elif overall == "MEASURED_OK":
            measured_ok.append(row)
        elif overall == "FAIL_FIRE_STARVED":
            fire_starved.append(row)

    # Sort by total fires (highest first) for diagnostic value
    too_freq_fail.sort(key=lambda r: r["long_total"] + r["short_total"], reverse=True)
    too_freq_borderline.sort(key=lambda r: r["long_total"] + r["short_total"], reverse=True)

    out = {
        "batch": "B716-FIRE-COUNT-CEILING-CLASSIFICATION",
        "input_file": str(input_path),
        "params": {
            "ceiling_per_year_per_direction": ceiling,
            "borderline_per_year_per_direction": borderline,
            "window_years": window_years,
            "starved_threshold_per_year": 30,
        },
        "summary": {
            "n_strategies_total": len(classifications),
            "n_too_freq_fail": len(too_freq_fail),
            "n_too_freq_borderline": len(too_freq_borderline),
            "n_measured_ok": len(measured_ok),
            "n_fire_starved": len(fire_starved),
            "n_both_zero": len([c for c in classifications if c["overall"] == "BOTH_ZERO"]),
        },
        "too_frequent_fail": too_freq_fail,
        "too_frequent_borderline": too_freq_borderline,
        "all_classifications": classifications,
    }

    with open(output_path, "w") as f:
        json.dump(out, f, indent=2)

    # Print summary
    print("=" * 80)
    print(f"FIRE-COUNT CEILING CLASSIFICATION (ceiling={ceiling}/yr/dir, window={window_years}yr)")
    print("=" * 80)
    print(f"Total strategies: {out['summary']['n_strategies_total']}")
    print(f"  TOO_FREQUENT_FAIL:       {out['summary']['n_too_freq_fail']}")
    print(f"  TOO_FREQUENT_BORDERLINE: {out['summary']['n_too_freq_borderline']}")
    print(f"  MEASURED_OK:             {out['summary']['n_measured_ok']}")
    print(f"  FAIL_FIRE_STARVED:       {out['summary']['n_fire_starved']}")
    print(f"  BOTH_ZERO:               {out['summary']['n_both_zero']}")
    print()
    if too_freq_fail:
        print(f"TOO_FREQUENT_FAIL ({len(too_freq_fail)} strategies, fires >{ceiling}/yr/direction):")
        for r in too_freq_fail:
            print(f"  {r['strategy']:50} L={r['long_per_year']:>8.0f}/yr [{r['long_class']:24}]  S={r['short_per_year']:>8.0f}/yr [{r['short_class']:24}]")
        print()
    if too_freq_borderline:
        print(f"TOO_FREQUENT_BORDERLINE ({len(too_freq_borderline)} strategies, fires {borderline:.0f}-{ceiling:.0f}/yr/direction):")
        for r in too_freq_borderline:
            print(f"  {r['strategy']:50} L={r['long_per_year']:>8.0f}/yr  S={r['short_per_year']:>8.0f}/yr")
        print()
    print(f"Output: {output_path}")
    return 0


def _classify_single(per_yr: float, ceiling: float, borderline: float, threshold_min: int) -> str:
    if per_yr == 0:
        return "ZERO"
    if per_yr < threshold_min:
        return "FAIL_FIRE_STARVED"
    if per_yr > ceiling:
        return "TOO_FREQUENT_FAIL"
    if per_yr > borderline:
        return "TOO_FREQUENT_BORDERLINE"
    return "MEASURED_OK"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default="output_audit/fire_count_measured_b660_post_b689_extended.json")
    ap.add_argument("--ceiling-per-year-per-direction", type=float, default=5000.0)
    ap.add_argument("--window-years", type=float, default=6.41)
    ap.add_argument("--output", default="output_audit/fire_count_ceiling_classification_b716.json")
    args = ap.parse_args()
    input_path = REPO / args.input if not Path(args.input).is_absolute() else Path(args.input)
    output_path = REPO / args.output if not Path(args.output).is_absolute() else Path(args.output)
    return classify(input_path, args.ceiling_per_year_per_direction, args.window_years, output_path)


if __name__ == "__main__":
    sys.exit(main())
