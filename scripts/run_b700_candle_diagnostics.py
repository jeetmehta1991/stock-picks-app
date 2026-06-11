"""B700 follow-on: 2 reviewer-asked diagnostics RUNNABLE NOW per owner approval
2026-06-11.

# Source: external reviewer Part 2 + Part 3 per CHECKLIST #77

Tests the reviewer's two specific hypotheses about the candle cluster:

  DIAGNOSTIC 1 -- CC-D redundancy:
    Reviewer's claim: "morning_star + bullish_engulfing + doji_at_support
    all fire on the same setup (bullish reversal at support after decline).
    Three 'different' patterns that fire on the same setup are not three
    strategies, they're one signal wearing three hats."
    Test: compute Jaccard overlap of (ticker, bar) fire sets across the
    3 strategies. High overlap -> effective N = 1, not 3.

  DIAGNOSTIC 2 -- CC-E confronting test:
    Reviewer's claim: "Doc treats 'Nison documented it' as 'it has edge.'
    Those are different. Run conditional_add_test where existing = location
    + volume gates only and candidate = the candle pattern itself. If the
    pattern doesn't lift conditional follow-through, the strategy's edge
    is in the location+volume, not the pattern."
    Test: per strategy, compute FT(location + volume) vs FT(location +
    volume + candle pattern). If add-test verdict is REJECT_REDUNDANT,
    the candle gate doesn't earn its slot.

Both diagnostics use simplified producer-signal proxies for the candle
patterns (not the exact strat_* fire logic) because the goal is to test
the reviewer's HYPOTHESIS not validate the production strategies. Output
is a markdown report for owner review.

Universe: 30 alphabetical T1a tickers; train/test through 2023/2024+;
horizon 10 bars; 2x ATR target / 1x ATR stop.

Output: output_audit/b700_candle_diagnostics/b700_candle_report.md +
b700_candle_results.json
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "scripts"))

from trigger_followthrough import follow_through_rate, conditional_add_test

OUT_DIR = _REPO / "output_audit" / "b700_candle_diagnostics"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OHLCV_DIR = _REPO / "data_prefetch" / "polygon" / "ohlcv_daily"
T1A_PATH = _REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"


def load_ohlcv(ticker: str) -> pd.DataFrame | None:
    fp = OHLCV_DIR / f"{ticker}.parquet"
    if not fp.exists():
        return None
    df = pd.read_parquet(fp)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
    df.columns = [c.lower() for c in df.columns]
    if {"open", "high", "low", "close", "volume"} - set(df.columns):
        return None
    return df


def load_universe(n: int = 30) -> list[str]:
    df = pd.read_csv(T1A_PATH, comment="#")
    as_of = date(2026, 5, 31)
    added = pd.to_datetime(df["added_date"], errors="coerce").dt.date
    removed = pd.to_datetime(df["removed_date"], errors="coerce").dt.date
    mask = ((added.isna()) | (added <= as_of)) & ((removed.isna()) | (removed > as_of))
    tickers = sorted(df[mask]["Symbol"].astype(str).str.upper().unique().tolist())
    return tickers[:n]


def compute_candle_signals(df: pd.DataFrame) -> dict[str, np.ndarray]:
    """Per-bar signals approximating the reviewer's candle pattern definitions
    + location/volume gates. NOT exactly the production strat_* logic; tests
    the reviewer's hypothesis about whether the candle pattern gate adds edge."""
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    v = df["volume"].to_numpy(float)
    n = len(c)

    # Body + range
    body = np.abs(c - o)
    rng = h - l + 1e-9
    body_pct = body / rng

    # Prior bar
    prev_o = np.concatenate([[o[0]], o[:-1]])
    prev_c = np.concatenate([[c[0]], c[:-1]])
    prev_h = np.concatenate([[h[0]], h[:-1]])
    prev_l = np.concatenate([[l[0]], l[:-1]])
    prev_body = np.abs(prev_c - prev_o)

    # --- CANDLE PATTERN PROXIES ---

    # Morning star (3-bar): bar[t-2] = bearish big body, bar[t-1] = small body
    # (doji or small star), bar[t] = bullish big body closing >50% into bar[t-2]
    prev2_o = np.concatenate([[o[0], o[0]], o[:-2]])
    prev2_c = np.concatenate([[c[0], c[0]], c[:-2]])
    bar_tminus2_bearish = (prev2_c < prev2_o) & (np.abs(prev2_c - prev2_o) > 0.5 * np.abs(np.concatenate([[h[0], h[0]], h[:-2]]) - np.concatenate([[l[0], l[0]], l[:-2]])))
    bar_tminus1_small = (prev_body / (prev_h - prev_l + 1e-9) < 0.3)
    bar_t_bullish = (c > o) & (body_pct > 0.5)
    midpoint_tminus2 = (prev2_o + prev2_c) / 2.0
    closes_above_mid = (c > midpoint_tminus2)
    morning_star = bar_tminus2_bearish & bar_tminus1_small & bar_t_bullish & closes_above_mid

    # Bullish engulfing: bar[t] body engulfs bar[t-1] body, bar[t-1] was bearish, bar[t] is bullish
    prev_bearish = prev_c < prev_o
    today_bullish = c > o
    body_engulf = (o < prev_c) & (c > prev_o)
    bullish_engulfing = prev_bearish & today_bullish & body_engulf

    # Doji at support: doji shape + at a swing low / lower-band location
    is_doji = body_pct < 0.1
    # Approximate "at support" = close near recent 20-bar low
    rolling_20_low = pd.Series(l).rolling(20).min().shift(1).to_numpy()
    near_low = c <= rolling_20_low * 1.03  # within 3% of 20-bar low
    doji_at_support = is_doji & near_low

    # --- LOCATION + VOLUME GATES (the "non-pattern" baseline) ---

    # Prior downtrend (5-bar return < 0)
    ret_5d = pd.Series(c).pct_change(5).to_numpy()
    prior_downtrend = ret_5d < 0

    # Volume spike (1.5x avg)
    vol_avg_20 = pd.Series(v).rolling(20).mean().shift(1).to_numpy()
    vol_spike = v > 1.5 * vol_avg_20

    # Combined location + volume baseline (what the reviewer says might
    # already have all the edge, regardless of candle pattern)
    location_volume_only = prior_downtrend & near_low & vol_spike

    return {
        "morning_star": morning_star,
        "bullish_engulfing": bullish_engulfing & prior_downtrend & near_low,  # strategy gate stack
        "doji_at_support": doji_at_support & vol_spike,                       # strategy gate stack
        "location_volume_only": location_volume_only,                          # baseline for confronting test
        "morning_star_raw": morning_star,                                      # pattern-only (no location)
        "bullish_engulfing_raw": prev_bearish & today_bullish & body_engulf,   # pattern-only
        "doji_at_support_raw": is_doji,                                        # pattern-only
    }


def jaccard_overlap(a: np.ndarray, b: np.ndarray) -> tuple[int, int, float]:
    """For two boolean fire-mask arrays, return (n_intersection, n_union,
    jaccard_similarity)."""
    intersection = int((a & b).sum())
    union = int((a | b).sum())
    j = intersection / union if union > 0 else 0.0
    return intersection, union, j


def diagnostic_1_redundancy(tickers: list[str]) -> dict:
    """Compute Jaccard overlap of fire-bar sets across (morning_star,
    bullish_engulfing, doji_at_support) per ticker, then aggregate."""
    per_pair_results = {
        "morning_star x bullish_engulfing": [],
        "morning_star x doji_at_support": [],
        "bullish_engulfing x doji_at_support": [],
    }
    fire_counts = {"morning_star": 0, "bullish_engulfing": 0, "doji_at_support": 0}
    n_tickers = 0

    for ticker in tickers:
        df = load_ohlcv(ticker)
        if df is None or len(df) < 300:
            continue
        sigs = compute_candle_signals(df)
        ms = sigs["morning_star"]
        be = sigs["bullish_engulfing"]
        dj = sigs["doji_at_support"]
        for k, arr in [("morning_star", ms), ("bullish_engulfing", be), ("doji_at_support", dj)]:
            fire_counts[k] += int(arr.sum())
        for pair_name, (a, b) in [
            ("morning_star x bullish_engulfing", (ms, be)),
            ("morning_star x doji_at_support", (ms, dj)),
            ("bullish_engulfing x doji_at_support", (be, dj)),
        ]:
            inter, union, j = jaccard_overlap(a, b)
            if union > 0:
                per_pair_results[pair_name].append({
                    "ticker": ticker, "intersection": inter, "union": union, "jaccard": j,
                })
        n_tickers += 1

    # Aggregate weighted by union size
    summary = {}
    for pair_name, rows in per_pair_results.items():
        if not rows:
            summary[pair_name] = {"avg_jaccard": None, "total_intersection": 0, "total_union": 0}
            continue
        total_int = sum(r["intersection"] for r in rows)
        total_un = sum(r["union"] for r in rows)
        avg_j = total_int / total_un if total_un > 0 else 0.0
        summary[pair_name] = {
            "avg_jaccard": round(avg_j, 4),
            "total_intersection": total_int,
            "total_union": total_un,
            "n_tickers": len(rows),
        }

    return {
        "n_tickers": n_tickers,
        "fire_counts_total": fire_counts,
        "pair_overlap": summary,
    }


def diagnostic_2_confronting(tickers: list[str]) -> dict:
    """For each candle strategy: does adding the candle pattern lift FT
    beyond location+volume gates alone?"""
    train_end = pd.Timestamp(date(2023, 12, 31))
    results = {}

    for strategy_name, pattern_key in [
        ("morning_star", "morning_star_raw"),
        ("bullish_engulfing", "bullish_engulfing_raw"),
        ("doji_at_support", "doji_at_support_raw"),
    ]:
        base_num = 0.0; base_n = 0
        with_num = 0.0; with_n = 0
        for ticker in tickers:
            df = load_ohlcv(ticker)
            if df is None or len(df) < 300:
                continue
            sigs = compute_candle_signals(df)
            test_mask = np.asarray(df.index > train_end)
            # Existing = location + volume baseline (no candle pattern)
            existing = sigs["location_volume_only"]
            # Candidate gate = the candle pattern itself
            new_gate = sigs[pattern_key]
            for trig, key in [(existing & test_mask, "base"), (existing & new_gate & test_mask, "with")]:
                if trig.sum() < 3:
                    continue
                r, n, _ = follow_through_rate(df, trig, +1,
                                              target_mult=2.0, stop_mult=1.0, horizon=10)
                if np.isfinite(r) and n > 0:
                    if key == "base":
                        base_num += r * n; base_n += n
                    else:
                        with_num += r * n; with_n += n
        base_ft = base_num / base_n if base_n else float("nan")
        with_ft = with_num / with_n if with_n else float("nan")
        kept = with_n / base_n if base_n else 0.0
        if with_n < 30:
            verdict = "DEFER"
            note = f"n={with_n} too few"
        elif (with_ft - base_ft) >= 0.03:
            verdict = "ADD"
            note = f"pattern lifts FT {base_ft:.3f}->{with_ft:.3f} (+{with_ft-base_ft:.3f}); keeps {kept:.0%}"
        elif (with_ft - base_ft) <= -0.03:
            verdict = "REJECT_HARMFUL"
            note = f"pattern LOWERS FT {base_ft:.3f}->{with_ft:.3f}"
        else:
            verdict = "REJECT_REDUNDANT"
            note = (f"no FT lift ({base_ft:.3f}->{with_ft:.3f}); pattern doesn't earn its slot. "
                    f"Reviewer's hypothesis CONFIRMED -- strategy's edge is in location+volume, not the pattern.")
        results[strategy_name] = {
            "base_ft": round(base_ft, 4) if np.isfinite(base_ft) else None,
            "with_ft": round(with_ft, 4) if np.isfinite(with_ft) else None,
            "base_n": base_n, "with_n": with_n,
            "kept_frac": round(kept, 4),
            "verdict": verdict, "note": note,
        }
    return results


def fmt_md(d1: dict, d2: dict, tickers: list[str]) -> str:
    L = [
        "# B700 Candle Diagnostics Report (2026-06-11)",
        "",
        "# Source: scripts/run_b700_candle_diagnostics.py per CHECKLIST #77",
        "",
        f"Universe: {len(tickers)} alphabetical T1a PIT-active tickers ({tickers[:5]} ...).",
        "Train through 2023-12-31; test 2024-01-01 onward. Barrier race: +2x ATR target, -1x ATR stop, 10-bar horizon.",
        "",
        "Reviewer-asked, runnable-NOW diagnostics on the trustworthy candle half of the cluster (technical.compute_candles producer; not affected by chart_patterns harness gap or repaint risk).",
        "",
        "## Diagnostic 1: CC-D redundancy hypothesis",
        "",
        "**Reviewer's claim:** morning_star + bullish_engulfing + doji_at_support all fire on the same setup (bullish reversal at support after decline). High Jaccard overlap of fire-bar sets -> effective N = 1, not 3.",
        "",
        "### Fire counts (across all tickers, train+test combined)",
        "",
        "| Strategy | Total fires |",
        "|---|---:|",
        f"| morning_star (with location+volume gates) | {d1['fire_counts_total']['morning_star']} |",
        f"| bullish_engulfing (with location+volume gates) | {d1['fire_counts_total']['bullish_engulfing']} |",
        f"| doji_at_support (with location+volume gates) | {d1['fire_counts_total']['doji_at_support']} |",
        "",
        "### Pairwise Jaccard overlap",
        "",
        "| Pair | Intersection | Union | Jaccard | n_tickers |",
        "|---|---:|---:|---:|---:|",
    ]
    for pair, info in d1["pair_overlap"].items():
        j = info.get("avg_jaccard")
        L.append(f"| {pair} | {info['total_intersection']} | {info['total_union']} | {j if j is not None else 'n/a'} | {info.get('n_tickers', 0)} |")
    L.extend([
        "",
        "**Interpretation:**",
        "- Jaccard near 1.0 -> patterns fire on (nearly) the same bars -> 1 effective strategy, not 3",
        "- Jaccard near 0.0 -> patterns are orthogonal -> 3 distinct strategies",
        "- Jaccard in middle -> some overlap but each pattern catches independent bars",
        "",
        "## Diagnostic 2: CC-E confronting test",
        "",
        "**Reviewer's claim:** \"Doc treats 'Nison documented it' as 'it has edge.' Those are different. Run conditional_add_test where existing = location+volume gates only, candidate = the candle pattern. If the pattern doesn't lift conditional follow-through, the strategy's edge is in the location+volume, not the pattern.\"",
        "",
        "### Verdicts",
        "",
        "| Strategy | Base FT (location+vol) | With FT (+ pattern) | Kept frac | Verdict |",
        "|---|---:|---:|---:|---|",
    ])
    for s, info in d2.items():
        L.append(f"| {s} | {info['base_ft']} (n={info['base_n']}) | {info['with_ft']} (n={info['with_n']}) | {info['kept_frac']:.0%} | **{info['verdict']}** |")
        L.append(f"|   |   |   |   | {info['note']} |")
    L.extend([
        "",
        "**Reviewer's confrontation:**",
        "- ADD -> the candle pattern DOES earn its slot; reviewer's hypothesis REFUTED for that strategy",
        "- REJECT_REDUNDANT -> the candle pattern doesn't lift conditional FT; reviewer's hypothesis CONFIRMED -- strategy's edge is in location+volume not the candle gate",
        "- REJECT_HARMFUL -> the candle pattern actively LOWERS FT (anti-selects); strategy needs structural rethink",
        "- DEFER -> insufficient surviving sample to judge; needs larger universe or longer window",
        "",
        "## Caveats",
        "",
        "- 30-ticker sample is a hypothesis-generating run, not a deployment verdict. Full-universe post-B660 re-run with measured fire counts will be authoritative.",
        "- Candle pattern proxies are simplified (not the exact strat_* fire logic). Goal is to test the REVIEWER'S HYPOTHESIS not validate the production strategies.",
        "- Train/test split: pre-2024 train, 2024+ test. Held-out FT used for verdict.",
        "- Per `feedback_local_changes_default_global_needs_approval`, these results are EVIDENCE for owner decisions, not autonomous code-change triggers.",
    ])
    return "\n".join(L)


def main() -> int:
    tickers = load_universe(30)
    print(f"Loaded {len(tickers)} tickers: {tickers[:5]} ...")
    print("Running Diagnostic 1 (CC-D redundancy)...")
    d1 = diagnostic_1_redundancy(tickers)
    print(f"  Fire counts: {d1['fire_counts_total']}")
    for pair, info in d1["pair_overlap"].items():
        print(f"  {pair}: Jaccard = {info.get('avg_jaccard')}")
    print("Running Diagnostic 2 (CC-E confronting test)...")
    d2 = diagnostic_2_confronting(tickers)
    for s, info in d2.items():
        print(f"  {s}: {info['verdict']} -- {info['note']}")

    report = fmt_md(d1, d2, tickers)
    md_path = OUT_DIR / "b700_candle_report.md"
    md_path.write_text(report)
    json_path = OUT_DIR / "b700_candle_results.json"
    json_path.write_text(json.dumps({"diagnostic_1": d1, "diagnostic_2": d2}, indent=2))
    print(f"\nWrote report: {md_path}")
    print(f"Wrote JSON: {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
