#!/usr/bin/env python
"""S6-B3134 - the PRE-REGISTERED, NON-GATING eligibility sensitivity for a
landed Step-2 cube (frozen B3135, 2026-09-29, before the span-9 holdout read).

The verdict of record is the landed family grade, UNCHANGED. This instrument
re-grades COPIES of the landed cube with rows removed and reports each variant
beside it. A variant can HOLD an admission (the owner rules first), never
create one: a canonical FAIL that passes under a variant is a RESCUE found by
trying extra paths and is reported only.

VARIANTS (the S6-B3134 rows' own definitions; every rule keyed on the SCREEN
DAY, which is the recorded entry_date - backtest.py:3622/3722 book entries
with entry_date=as_of and fill at the next open):
  b1     SBNY entries with entry_date > 2023-03-15 (its T1a removed_date).
  b2     FISV entries within its first 20 bars on/after 2025-11-11 (the first
         bar after the 610-day FISV->FI->FISV rename hole; 20 = the Bollinger
         period).
  b3     REMOVAL SIDE of daily S&P membership: a T1a-master ticker that is not
         a PIT member on its entry_date AND has a recorded removed_date on or
         before it. Clock: the DAILY membership table (get_sp500_constituents_pit,
         out on the removal date itself).
  b4     the OPEN-TRADE CARRY (S6-B3134a Leak 2): entries screened while the
         ticker was OUTSIDE its year's Jan-1 eligibility set - a replica of
         backtest.py:495-518 (>=30 bars, last close >= min_price, 20-bar mean
         volume >= min_avg_volume, T1a-master tickers must be PIT members on
         Jan 1). Clock: Jan 1 of the entry year. b3 and b4 use DIFFERENT
         clocks and overlap without either containing the other.
  union  b1 | b2 | b3 | b4.

METHOD, fail-closed at every step:
  1. hash the landed cube's two graded inputs before touching anything;
  2. REPRODUCE: grade an unfiltered copy with the battery's own argv
     (run_postconfig helpers, --out redirected to scratch) and require it to
     equal the landed grid on the selected exit, the verdict, every gate
     value, the holdout / full-period n, and the IS pick - else every variant
     is DIFFERS and nothing else is believed;
  3. per variant: print rows removed FIRST (a variant that removes nothing
     agrees by construction and is not reassurance), then grade the copy.
Outputs go to a scratch directory with non-cube names; nothing here writes
the landed cube, its grid, or output_audit.

--r5-reproduce re-derives the B3134b/B3135 measurement on the R5 trade log
(7,097 of 189,471 carry entries: 5,063 index / 1,915 volume / 119 price) so
the frozen b4 selector is shown to be the code that produced the numbers.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

B1_TICKER, B1_AFTER = "SBNY", dt.date(2023, 3, 15)
B2_TICKER, B2_FROM, B2_BARS = "FISV", dt.date(2025, 11, 11), 20
YEARS = (2022, 2023, 2024, 2025, 2026)
VARIANTS = ("b1", "b2", "b3", "b4", "union")
GATE_KEYS = ("pooled_sharpe", "profit_factor", "sortino", "psr",
             "min_trades_holdout", "min_trades_full_period")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def instrument_sha256() -> str:
    """This file's hash over LF-normalised bytes - the pre-registration pins
    it, and a checkout that rewrites line endings (L850) must not read as a
    changed instrument."""
    return hashlib.sha256(Path(__file__).read_bytes()
                          .replace(b"\r\n", b"\n")).hexdigest()


def _ohlcv(ticker: str, start: dt.date, end: dt.date):
    from backtest.data import cache as c
    df = c.get_ohlcv(ticker, start, end)
    if df is None or len(df) == 0:
        return None
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    return df


def jan1_sets(tickers, years=YEARS) -> tuple[dict, dict]:
    """Replica of backtest.py:495-518 - {year: eligible set} plus the reason
    each (ticker, year) failed. ONE loader per ticker, so peak memory stays
    one frame."""
    from backtest.config import LIQUIDITY, DATA_LOAD_START
    from backtest.data.universe import get_t1a_master_set, get_sp500_constituents_pit
    master = get_t1a_master_set()
    pit = {y: set(get_sp500_constituents_pit(dt.date(y, 1, 1))) for y in years}
    start = DATA_LOAD_START if isinstance(DATA_LOAD_START, dt.date) else \
        pd.Timestamp(DATA_LOAD_START).date()
    elig = {y: set() for y in years}
    why = {}
    for t in tickers:
        df = _ohlcv(t, start, dt.date(max(years), 12, 31))
        if df is None:
            for y in years:
                why[(t, y)] = "no-ohlcv"
            continue
        idx = df.index.date
        for y in years:
            sl = df[idx <= dt.date(y, 1, 1)]
            r = None
            if len(sl) < 30:
                r = "history<30"
            elif float(sl["close"].iloc[-1]) < LIQUIDITY["min_price"]:
                r = "price<min"
            elif float(sl["volume"].tail(20).mean()) < LIQUIDITY["min_avg_volume"]:
                r = "avgvol<min"
            elif master and t in master and t not in pit[y]:
                r = "not-in-PIT"
            if r is None:
                elig[y].add(t)
            else:
                why[(t, y)] = r
    return elig, why


def removal_table() -> tuple[set, dict]:
    """T1a master + each ticker's recorded removed_dates (for b3's removal
    side). Membership itself is asked of get_sp500_constituents_pit - one
    definition of 'member on day D' (L593)."""
    from backtest.data.universe import UNIVERSE_DIR, get_t1a_master_set
    f = UNIVERSE_DIR / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
    df = pd.read_csv(f, comment="#")
    rem = {}
    for sym, r in zip(df["Symbol"], df["removed_date"]):
        d = pd.to_datetime(r, errors="coerce")
        if pd.notna(d):
            rem.setdefault(str(sym), []).append(d.date())
    return get_t1a_master_set(), rem


def fisv_window() -> tuple[dt.date, dt.date] | None:
    df = _ohlcv(B2_TICKER, B2_FROM, dt.date(2026, 12, 31))
    if df is None:
        return None
    days = sorted(d for d in df.index.date if d >= B2_FROM)[:B2_BARS]
    return (days[0], days[-1]) if days else None


def classify(entries: pd.DataFrame) -> pd.DataFrame:
    """Per distinct (ticker, entry_date): one boolean column per variant plus
    the b4 reason. `entries` needs ticker and entry_date (date)."""
    from backtest.data.universe import get_sp500_constituents_pit
    e = entries[["ticker", "entry_date"]].drop_duplicates().copy()
    e["ticker"] = e["ticker"].astype(str)
    tickers = sorted(e["ticker"].unique())
    elig, why = jan1_sets(tickers)
    master, rem = removal_table()
    fw = fisv_window()
    pit_cache: dict = {}

    def member(t, d):
        if d not in pit_cache:
            pit_cache[d] = set(get_sp500_constituents_pit(d))
        return t in pit_cache[d]

    b1, b2, b3, b4, r4 = [], [], [], [], []
    for t, d in zip(e["ticker"], e["entry_date"]):
        b1.append(t == B1_TICKER and d > B1_AFTER)
        b2.append(bool(fw) and t == B2_TICKER and fw[0] <= d <= fw[1])
        b3.append(t in master and not member(t, d)
                  and any(x <= d for x in rem.get(t, [])))
        out = t not in elig.get(d.year, set())
        b4.append(out)
        r4.append(why.get((t, d.year), "-") if out else "")
    e["b1"], e["b2"], e["b3"], e["b4"], e["b4_reason"] = b1, b2, b3, b4, r4
    e["union"] = e["b1"] | e["b2"] | e["b3"] | e["b4"]
    return e


# ---------------------------------------------------------------- grading
def grader_argv(cube_copy: Path, landed: Path, out: Path) -> tuple[list, dict]:
    """The battery's own step-2 grader argv (run_postconfig.run_family),
    with --cube and --out redirected. Built from its helpers, not retyped."""
    import run_postconfig as rp
    manifest = rp.read_manifest(landed)
    graded, riders = rp.graded_and_riders(landed)
    strategies = rp.cube_strategies(landed)
    fam = graded if (graded and riders) else (
        strategies[0] if len(strategies) == 1 else None)
    if fam is None or fam not in rp.FAMILIES:
        raise SystemExit(f"[FAIL] no registered family for {landed} "
                         f"(graded={graded!r}, strategies={strategies})")
    tools = rp._tools(fam)
    p, why = rp.params_from_manifest(fam, manifest)
    if p is None:
        raise SystemExit(f"[FAIL] params: {why}")
    step, _ = rp.derive_step(manifest, step1_flag=False, step2_flag=False)
    gb = tools["grade"]
    s2 = []
    if step == 2 and gb.get("step2_flag"):
        s2.append(str(gb["step2_flag"]))
    pre = rp.preregistered_exit(manifest)
    if pre and gb.get("preregistered_flag"):
        s2 += [str(gb["preregistered_flag"]), pre]
    argv = [sys.executable, str(ROOT / "scripts" / gb["script"]),
            "--cube", rp._cube_arg(cube_copy, gb), *rp._flag_args(gb, tools, p),
            *list(gb.get("extra") or []), *s2, "--out", str(out)]
    env = rp._sub_env(rp._arm_env(manifest), gb)
    return argv, env


STEP2_VALUES = ("sharpe", "sortino", "psr", "profit_factor", "payoff",
                "expectancy", "win_rate", "p", "ci_lo", "margin")


def summarize(grid: dict) -> dict:
    """The verdict-bearing fields of a family grid (grade_bollinger_config
    grade_step2 shape: `gates` is {gate: bool}, values are top-level keys of
    the step2 block; step1_ranking[0] is the IS pick)."""
    s2 = grid.get("step2") if isinstance(grid.get("step2"), dict) else {}
    gates = s2.get("gates") if isinstance(s2.get("gates"), dict) else {}
    top = (grid.get("step1_ranking") or [None])[0] or {}
    return {
        "selected_exit": s2.get("selected_exit"),
        "verdict": s2.get("verdict"),
        "gates": {k: gates.get(k) for k in sorted(gates)},
        "values": {k: s2.get(k) for k in STEP2_VALUES},
        "holdout_n": s2.get("holdout_n"),
        "full_period_n": s2.get("full_period_n"),
        "is_stats": s2.get("is_stats"),
        "is_pick": {k: top.get(k) for k in ("exit", "is_sharpe", "is_ci_lo", "fires")},
        "is_rows": grid.get("is_rows"), "holdout_rows": grid.get("holdout_rows"),
    }


def _canon(x):
    if isinstance(x, float):
        return round(x, 9)
    if isinstance(x, dict):
        return {k: _canon(v) for k, v in sorted(x.items())}
    if isinstance(x, list):
        return [_canon(v) for v in x]
    return x


def grade_copy(landed: Path, ted: pd.DataFrame, work: Path, name: str) -> dict:
    d = work / f"sens_{name}"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    ted.to_csv(d / "trade_exit_detail.csv", index=False)
    shutil.copy2(landed / "run_manifest.json", d / "run_manifest.json")
    out = work / f"sens_{name}_grid.json"
    argv, env = grader_argv(d, landed, out)
    r = subprocess.run(argv, env=env, capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        return {"error": f"grader exit {r.returncode}",
                "tail": (r.stdout or "")[-600:] + (r.stderr or "")[-600:]}
    return summarize(json.loads(out.read_text(encoding="utf-8")))


def compare(canon: dict, var: dict) -> dict:
    if "error" in var:
        return {"differs": True, "why": "variant errored (fail closed)"}
    exit_d = var["selected_exit"] != canon["selected_exit"]
    verdict_d = var["verdict"] != canon["verdict"]
    keys = set(canon["gates"]) | set(var["gates"])
    flips = sorted(k for k in keys
                   if canon["gates"].get(k) != var["gates"].get(k))
    rescue = (canon["verdict"] != "PASS" and var["verdict"] == "PASS")
    return {"differs": bool(exit_d or verdict_d), "exit_differs": exit_d,
            "verdict_differs": verdict_d, "gate_pass_flips": flips,
            "rescue_report_only": rescue}


def run_landing(cube: Path, work: Path) -> dict:
    landed_grid = ROOT / "output_audit" / f"{cube.name}_grid_auto.json"
    ted_path = cube / "trade_exit_detail.csv"
    for p in (ted_path, cube / "run_manifest.json", landed_grid):
        if not p.exists():
            raise SystemExit(f"[FAIL] missing {p}")
    doc = {"instrument": "scripts/eligibility_sensitivity.py (S6-B3134)",
           "instrument_sha256_lf": instrument_sha256(),
           "cube": str(cube).replace("\\", "/"),
           "inputs_sha256": {"trade_exit_detail.csv": sha256(ted_path),
                             "run_manifest.json": sha256(cube / "run_manifest.json"),
                             "landed_grid": sha256(landed_grid)},
           "verdict_of_record": str(landed_grid).replace("\\", "/")}
    ted = pd.read_csv(ted_path, low_memory=False)
    ted["_d"] = pd.to_datetime(ted["entry_date"].astype(str).str[:10]).dt.date
    cls = classify(pd.DataFrame({"ticker": ted["ticker"].astype(str),
                                 "entry_date": ted["_d"]}))
    key = cls.set_index(["ticker", "entry_date"])
    canon = summarize(json.loads(landed_grid.read_text(encoding="utf-8")))
    doc["canonical"] = canon
    work.mkdir(parents=True, exist_ok=True)
    rep = grade_copy(cube, ted.drop(columns=["_d"]), work, "b0_unfiltered")
    ok = "error" not in rep and _canon(rep) == _canon(canon)
    doc["reproduction"] = {"ok": ok, "unfiltered_copy": rep}
    doc["variants"] = {}
    tk = list(zip(ted["ticker"].astype(str), ted["_d"]))
    for v in VARIANTS:
        flags = [bool(key.at[(t, d), v]) for t, d in tk]
        drop = pd.Series(flags, index=ted.index)
        entries = cls[cls[v]]
        row = {"entries_removed": int(len(entries)),
               "exit_rows_removed": int(drop.sum()),
               "entries_removed_by_reason": (entries["b4_reason"].value_counts().to_dict()
                                             if v == "b4" else None),
               "tickers": sorted(entries["ticker"].unique().tolist())[:40]}
        print(f"[{v}] removes {row['entries_removed']} entries / "
              f"{row['exit_rows_removed']} exit rows", flush=True)
        if not ok:
            row["result"] = {"error": "reproduction failed - not graded"}
            row["compare"] = {"differs": True, "why": "reproduction failed (fail closed)"}
        else:
            res = grade_copy(cube, ted.loc[~drop].drop(columns=["_d"]), work, v)
            row["result"] = res
            row["compare"] = compare(canon, res)
        doc["variants"][v] = row
    doc["owner_rules_before_admission"] = any(
        r["compare"]["differs"] for r in doc["variants"].values())
    return doc


def r5_reproduce() -> dict:
    """The frozen b4 selector over R5's engine trades: must give 7,097 of
    189,471 (5,063 not-in-PIT / 1,915 avgvol / 119 price)."""
    f = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
    parts, tot = [], 0
    for ch in pd.read_csv(f, usecols=["ticker", "entry_date"], chunksize=200_000,
                          low_memory=True):
        tot += len(ch)
        parts.append(ch)
    tl = pd.concat(parts)
    tl["entry_date"] = pd.to_datetime(tl["entry_date"].astype(str).str[:10]).dt.date
    tickers = sorted(tl["ticker"].astype(str).unique())
    elig, why = jan1_sets(tickers)
    out = [t not in elig.get(d.year, set())
           for t, d in zip(tl["ticker"].astype(str), tl["entry_date"])]
    L = tl[out]
    reasons = pd.Series([why.get((t, d.year), "?") for t, d in
                         zip(L["ticker"].astype(str), L["entry_date"])]).value_counts()
    return {"trades_total": int(tot), "b4_trades": int(len(L)),
            "b4_by_reason": {k: int(v) for k, v in reasons.items()},
            "b4_tickers": int(L["ticker"].nunique())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cube", help="the LANDED cube dir")
    ap.add_argument("--work", help="scratch dir (never output_audit)")
    ap.add_argument("--out", help="summary JSON path")
    ap.add_argument("--r5-reproduce", action="store_true")
    ap.add_argument("--expect-instrument-sha", default=None,
                    help="the pre-registered LF-normalised sha256; refuse on mismatch")
    a = ap.parse_args(argv)
    got = instrument_sha256()
    if a.expect_instrument_sha is not None and got != a.expect_instrument_sha:
        print(f"REFUSED: instrument sha256 {got} != pre-registered "
              f"{a.expect_instrument_sha} - this is not the frozen S6-B3134 "
              "instrument (fail closed)")
        return 4
    if a.r5_reproduce:
        res = r5_reproduce()
        print(json.dumps(res, indent=1))
        want = {"trades_total": 189471, "b4_trades": 7097}
        good = all(res[k] == v for k, v in want.items()) and \
            res["b4_by_reason"] == {"not-in-PIT": 5063, "avgvol<min": 1915, "price<min": 119}
        print("R5 REPRODUCTION:", "OK" if good else "MISMATCH")
        return 0 if good else 3
    if not (a.cube and a.work and a.out):
        ap.error("--cube, --work and --out are required (or --r5-reproduce)")
    work = Path(a.work)
    if "output_audit" in work.resolve().parts:
        ap.error("--work must not be under output_audit (L880)")
    doc = run_landing(Path(a.cube), work)
    Path(a.out).write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")
    print("reproduction:", "OK" if doc["reproduction"]["ok"] else "FAILED (all variants DIFFERS)")
    for v, r in doc["variants"].items():
        c = r["compare"]
        print(f"  {v:6s} differs={c['differs']} exit={c.get('exit_differs')} "
              f"verdict={c.get('verdict_differs')} flips={c.get('gate_pass_flips')}")
    print("OWNER RULES BEFORE ADMISSION:", doc["owner_rules_before_admission"])
    return 0 if doc["reproduction"]["ok"] else 3


if __name__ == "__main__":
    sys.exit(main())
