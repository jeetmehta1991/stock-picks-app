"""S6-B3263 (B3139q-r90, L952): which CLOSED trade-log fires have NO row in
the exit cube - measured per fire, by the property a drop corrupts, never by
the symptom that first drew attention.

S6-B2649c's RCA (B2675) took a strategy with ZERO exit-cube rows as its
membership test and measured 14 strategies, 84 fires, on R5. The class it
named - a chunk replay erasing a strategy's rows when the chunk held too few
of its trades (B2046's incident) - also drops PART of a strategy: measured at
B3139q-r89 on output_r5_merged_1_7, 349 of 189,471 closed fires carry no
exit row, 265 of them in 62 strategies that kept others (S6-B3258).

For a cube dir holding trade_log.csv and trade_exit_detail.csv, per strategy:
closed fires (exit_date present; one per strategy x ticker x entry_date) and
those with any exit-cube row - WHOLE drops (none kept) and PARTIAL drops
(some kept). And the (strategy, ticker) pairs holding a missing fire, split
into SPLIT (another of the pair's fires kept) and WHOLLY missing: when a
run's chunks partition tickers, a per-chunk erasure keeps every pair whole,
so a SPLIT pair is evidence against it (S6-B3258's falsification test).

Read-only on the cube; --out writes the JSON. Refuses (exit 2) when either
file is missing or the trade log lacks a needed column.

    python scripts/exit_cube_coverage.py --cube-dir output_r5_merged_1_7
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_TL_COLS = ("strategy", "ticker", "entry_date", "exit_date")
_CUBE_COLS = ("strategy", "ticker", "entry_date")


def coverage(cube_dir, label=None, cube_df=None) -> dict:
    """The coverage record for one cube dir (see the module docstring).
    `label` is what the record names the cube by (the CLI passes the
    argument as given, so a committed record carries no machine path).
    `cube_df` is the exit cube already in memory (the battery's checks()
    loads it - S6-B3267), so the file is not read a second time."""
    import pandas as pd

    cube_dir = Path(cube_dir)
    tl_path = cube_dir / "trade_log.csv"
    cube_path = cube_dir / "trade_exit_detail.csv"
    for f in (tl_path, cube_path):
        if not f.is_file():
            raise FileNotFoundError(f"{f} missing - coverage needs both files")
    head = list(pd.read_csv(tl_path, nrows=0).columns)
    lacking = [c for c in _TL_COLS if c not in head]
    if lacking:
        raise ValueError(f"{tl_path.name} lacks {lacking}")
    parts = [ch for ch in pd.read_csv(tl_path, low_memory=False, chunksize=200_000,
                                       usecols=list(_TL_COLS))]
    tl = (pd.concat(parts, ignore_index=True) if parts
          else pd.DataFrame(columns=list(_TL_COLS)))
    tl = tl[tl["exit_date"].notna()].drop_duplicates(["strategy", "ticker", "entry_date"])
    keys = set()
    chunks = ([cube_df] if cube_df is not None else
              pd.read_csv(cube_path, low_memory=False, chunksize=1_000_000,
                          usecols=list(_CUBE_COLS)))
    for ch in chunks:
        keys.update(zip(ch["strategy"], ch["ticker"], ch["entry_date"].astype(str)))
    tl = tl.assign(in_cube=[(s, t, str(e)) in keys for s, t, e in
                            zip(tl["strategy"], tl["ticker"], tl["entry_date"])])
    strategies = {}
    for name, g in tl.groupby("strategy"):
        n, k = len(g), int(g["in_cube"].sum())
        strategies[str(name)] = {"closed": n, "covered": k, "missing": n - k,
                                 "kind": ("complete" if k == n else
                                          "whole" if k == 0 else "partial")}
    pair = tl.groupby(["strategy", "ticker"])["in_cube"].agg(["size", "sum"])
    holding = pair[pair["size"] > pair["sum"]]
    split = holding[holding["sum"] > 0]
    return {
        "cube_dir": str(label) if label is not None else str(cube_dir),
        "closed_fires": int(len(tl)),
        "covered": int(tl["in_cube"].sum()),
        "missing": int((~tl["in_cube"]).sum()),
        "whole": sorted(s for s, r in strategies.items() if r["kind"] == "whole"),
        "partial": sorted(s for s, r in strategies.items() if r["kind"] == "partial"),
        "pairs_with_missing": int(len(holding)),
        "pairs_split": int(len(split)),
        "pairs_wholly_missing": int(len(holding) - len(split)),
        "strategies": strategies,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cube-dir", required=True,
                    help="a dir holding trade_log.csv and trade_exit_detail.csv")
    ap.add_argument("--out", help="write the coverage record here (JSON)")
    a = ap.parse_args(argv)
    cube = Path(a.cube_dir)
    if not cube.is_absolute():
        cube = ROOT / cube
    try:
        rec = coverage(cube, label=a.cube_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(f"REFUSED (exit_cube_coverage, S6-B3263): {exc}")
        return 2
    whole_fires = sum(rec["strategies"][s]["missing"] for s in rec["whole"])
    part_fires = sum(rec["strategies"][s]["missing"] for s in rec["partial"])
    print(f"{rec['cube_dir']}: {rec['missing']} of {rec['closed_fires']} closed fires "
          f"carry no exit-cube row - WHOLE drops {len(rec['whole'])} strategies "
          f"({whole_fires} fires), PARTIAL drops {len(rec['partial'])} strategies "
          f"({part_fires} fires); (strategy, ticker) pairs holding a missing fire "
          f"{rec['pairs_with_missing']}: SPLIT {rec['pairs_split']}, wholly missing "
          f"{rec['pairs_wholly_missing']}")
    if a.out:
        Path(a.out).write_text(json.dumps(rec, indent=1), encoding="utf-8")
        print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
