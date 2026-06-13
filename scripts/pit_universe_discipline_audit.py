# Source: B747 + owner question 2026-06-13 "why does there need to be any delisting?" per CHECKLIST #77
"""
pit_universe_discipline_audit.py
================================

B747 PIT-DISCIPLINE AUDIT (reframed scope).

The owner's question 2026-06-13 -- "why does there need to be any delisting?" --
correctly pushed back on the original B747 framing of "calibrate the bias
direction". The right framing is empirical: T1a ALREADY tracks historical
delisting via `removed_date`. The actual question is whether every engine
honors the PIT universe at each per-bar as_of, or whether some engines
collapse to the END-snapshot (current S&P 500).

A direct read of the two consumers shows a DISCREPANCY:
  - backtest/engine/backtest.py:332 -- uses `get_sp500_constituents_pit(ref_date)`
    to build a per-year liquid set with PIT intersection. PIT-correct.
  - scripts/measure_fire_count.py:593 -- `tickers_full = _load_t1a_tickers(end)`.
    PIT filter applied at END date -> universe collapses to END-snapshot.
    Silently excludes 111 historical-removed names from every B660 measurement.

This audit produces a finding-grade report covering:
  1. T1a roster composition (active vs historical-removed)
  2. OHLCV coverage for each historical-removed name
  3. Per-consumer PIT-discipline verdict
  4. Estimated impact: # of (ticker, bar) cells silently excluded by
     measure_fire_count.py vs the PIT-honest count

USAGE
-----
    python scripts/pit_universe_discipline_audit.py
    python scripts/pit_universe_discipline_audit.py --start 2020-01-01 --end 2026-05-31
"""
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT_DIR = _REPO / "output_audit" / "b747_pit_discipline_audit"
OUT_DIR.mkdir(parents=True, exist_ok=True)

T1A_PATH = _REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
OHLCV_DIR = _REPO / "data_prefetch" / "polygon" / "ohlcv_daily"


# ----------------------------------------------------------------------------
# T1a roster + coverage probes
# ----------------------------------------------------------------------------
@dataclass
class HistoricalTicker:
    symbol: str
    company: str
    removed_date: date
    ohlcv_exists: bool
    ohlcv_first_bar: date | None = None
    ohlcv_last_bar: date | None = None
    ohlcv_n_bars: int = 0
    coverage_through_removal: bool = False  # has bars on or after removed_date - 1d


@dataclass
class ConsumerAuditRow:
    consumer: str         # filename:lineno
    universe_load_pattern: str  # "PIT_PER_BAR" | "PIT_PER_YEAR" | "PIT_AT_END_DATE" | "NO_PIT"
    verdict: str          # "PIT_CORRECT" | "PIT_INCORRECT" | "PARTIAL"
    note: str = ""


@dataclass
class AuditReport:
    t1a_total: int = 0
    t1a_active: int = 0
    t1a_historical_removed: int = 0
    ohlcv_present_for_removed: int = 0
    ohlcv_missing_for_removed: list = field(default_factory=list)
    historical_tickers: list = field(default_factory=list)  # list[HistoricalTicker]
    consumers: list = field(default_factory=list)           # list[ConsumerAuditRow]
    estimated_excluded_ticker_bars: int = 0
    note: str = ""


def _load_t1a() -> pd.DataFrame:
    df = pd.read_csv(T1A_PATH, comment="#")
    df["added_date_dt"] = pd.to_datetime(df["added_date"], errors="coerce").dt.date
    df["removed_date_dt"] = pd.to_datetime(df["removed_date"], errors="coerce").dt.date
    return df


def _probe_ohlcv(symbol: str, removed_date: date | None) -> HistoricalTicker:
    fpath = OHLCV_DIR / f"{symbol}.parquet"
    if not fpath.exists():
        return HistoricalTicker(
            symbol=symbol, company="", removed_date=removed_date,  # type: ignore[arg-type]
            ohlcv_exists=False,
        )
    try:
        df = pd.read_parquet(fpath)
    except Exception:
        return HistoricalTicker(
            symbol=symbol, company="", removed_date=removed_date,  # type: ignore[arg-type]
            ohlcv_exists=True, ohlcv_n_bars=-1,
        )
    if "date" in df.columns:
        dates = pd.to_datetime(df["date"], errors="coerce").dt.date.dropna()
    elif hasattr(df.index, "date"):
        dates = pd.Series(df.index.date)
    else:
        dates = pd.Series([], dtype=object)
    if dates.empty:
        return HistoricalTicker(
            symbol=symbol, company="", removed_date=removed_date,  # type: ignore[arg-type]
            ohlcv_exists=True,
        )
    first = dates.min()
    last = dates.max()
    coverage_through = (removed_date is None) or (last >= (pd.Timestamp(removed_date) - pd.Timedelta(days=1)).date())
    return HistoricalTicker(
        symbol=symbol, company="", removed_date=removed_date,  # type: ignore[arg-type]
        ohlcv_exists=True,
        ohlcv_first_bar=first, ohlcv_last_bar=last,
        ohlcv_n_bars=int(len(dates)),
        coverage_through_removal=bool(coverage_through),
    )


# ----------------------------------------------------------------------------
# Consumer-discipline static analysis
# ----------------------------------------------------------------------------
def _classify_consumer(filename: str, code: str) -> ConsumerAuditRow:
    """Static heuristic classification of how a consumer loads the universe.

    Pattern detection (in priority order):
      - 'get_sp500_constituents_pit' or 'get_t1a_pit_active' called per-bar/per-loop
        -> PIT_PER_BAR
      - Per-year refresh inside check_dates / annual loop
        -> PIT_PER_YEAR
      - _load_t1a_tickers(end) without per-bar refresh
        -> PIT_AT_END_DATE
      - No PIT references at all
        -> NO_PIT
    """
    # B748a (2026-06-13) recognize window-union loader as PIT_CORRECT. Check
    # this BEFORE the END-date heuristic so the new fix isn't mis-classified
    # by a comment that still contains `_load_t1a_tickers(end)`.
    if "_load_t1a_tickers_union_over_window" in code:
        # Verify the symbol is actually CALLED (not only defined or commented)
        # by stripping triple-quoted docstrings + line comments.
        import re as _re
        stripped = _re.sub(r'"""[\s\S]*?"""', '', code)
        stripped = _re.sub(r"'''[\s\S]*?'''", '', stripped)
        stripped = "\n".join(
            line.split("#", 1)[0] for line in stripped.splitlines()
        )
        if "_load_t1a_tickers_union_over_window(" in stripped:
            return ConsumerAuditRow(
                consumer=filename,
                universe_load_pattern="PIT_WINDOW_UNION",
                verdict="PIT_CORRECT",
                note="Window-union universe loader (B748a fix); historical-removed names included; per-bar PIT enforced via OHLCV truncation.",
            )
    if "get_sp500_constituents_pit" in code and ("check_dates" in code or "annual" in code or "for year" in code):
        return ConsumerAuditRow(
            consumer=filename,
            universe_load_pattern="PIT_PER_YEAR",
            verdict="PIT_CORRECT",
            note="Per-year PIT intersection via get_sp500_constituents_pit; survivor bias mitigated.",
        )
    if "_load_t1a_tickers(end" in code or "_load_t1a_tickers(args.end" in code:
        # Make sure this isn't matched only in a comment / docstring
        import re as _re
        stripped = _re.sub(r'"""[\s\S]*?"""', '', code)
        stripped = _re.sub(r"'''[\s\S]*?'''", '', stripped)
        stripped = "\n".join(
            line.split("#", 1)[0] for line in stripped.splitlines()
        )
        if "_load_t1a_tickers(end" in stripped or "_load_t1a_tickers(args.end" in stripped:
            return ConsumerAuditRow(
                consumer=filename,
                universe_load_pattern="PIT_AT_END_DATE",
                verdict="PIT_INCORRECT",
                note="Universe loaded with PIT filter at END date only. Historical-removed names excluded; END-snapshot survivor bias.",
            )
    if "get_t1a_pit_active" in code or "get_sp500_constituents_pit" in code:
        return ConsumerAuditRow(
            consumer=filename,
            universe_load_pattern="PIT_PER_BAR",
            verdict="PIT_CORRECT",
            note="Per-call PIT filter; universe respects historical removals.",
        )
    return ConsumerAuditRow(
        consumer=filename,
        universe_load_pattern="NO_PIT",
        verdict="PARTIAL",
        note="No PIT pattern detected; manual review required.",
    )


def _audit_consumers() -> list[ConsumerAuditRow]:
    targets = {
        "scripts/measure_fire_count.py": _REPO / "scripts" / "measure_fire_count.py",
        "backtest/engine/backtest.py":   _REPO / "backtest" / "engine" / "backtest.py",
        "backtest/run_phase1a.py":       _REPO / "backtest" / "run_phase1a.py",
    }
    out: list[ConsumerAuditRow] = []
    for name, path in targets.items():
        if not path.exists():
            out.append(ConsumerAuditRow(
                consumer=name, universe_load_pattern="(file missing)",
                verdict="ERROR", note="file not found",
            ))
            continue
        code = path.read_text(encoding="utf-8")
        out.append(_classify_consumer(name, code))
    return out


# ----------------------------------------------------------------------------
# Top-level audit
# ----------------------------------------------------------------------------
def audit_pit_discipline(start: date | None = None, end: date | None = None) -> AuditReport:
    if start is None:
        start = date(2020, 1, 1)
    if end is None:
        end = date(2026, 5, 31)

    df = _load_t1a()
    n_total = len(df)
    removed_mask = df["removed_date_dt"].notna()
    n_active = int((~removed_mask).sum())
    n_removed = int(removed_mask.sum())

    historical_rows: list[HistoricalTicker] = []
    ohlcv_missing: list[str] = []
    for _, row in df[removed_mask].iterrows():
        sym = str(row["Symbol"]).upper()
        ht = _probe_ohlcv(sym, row["removed_date_dt"])
        ht.company = str(row.get("Company", "")) if not pd.isna(row.get("Company")) else ""
        historical_rows.append(ht)
        if not ht.ohlcv_exists:
            ohlcv_missing.append(sym)

    consumers = _audit_consumers()

    # Estimate excluded ticker-bar count for the PIT_INCORRECT consumer:
    # for each historical-removed ticker, count bars in [start, removed_date].
    # If OHLCV missing, contributes 0.
    excluded = 0
    for ht in historical_rows:
        if not ht.ohlcv_exists or ht.ohlcv_n_bars == 0 or ht.removed_date is None:
            continue
        # bars between start and removed_date that the PIT-honest universe would have included
        # (we approximate via OHLCV last_bar capped at removed_date)
        eff_end = ht.removed_date
        if ht.ohlcv_last_bar and ht.ohlcv_last_bar < eff_end:
            eff_end = ht.ohlcv_last_bar
        if eff_end < start:
            continue
        # business days between start and eff_end
        n_bd = len(pd.bdate_range(max(start, ht.ohlcv_first_bar or start), eff_end))
        excluded += n_bd

    return AuditReport(
        t1a_total=n_total,
        t1a_active=n_active,
        t1a_historical_removed=n_removed,
        ohlcv_present_for_removed=n_removed - len(ohlcv_missing),
        ohlcv_missing_for_removed=sorted(ohlcv_missing),
        historical_tickers=historical_rows,
        consumers=consumers,
        estimated_excluded_ticker_bars=int(excluded),
    )


def render_report(rep: AuditReport, start: date, end: date) -> str:
    L = [
        "# B747 PIT-Universe Discipline Audit",
        "",
        "# Source: scripts/pit_universe_discipline_audit.py per CHECKLIST #77",
        "",
        "## Re-scoped from original B747 framing per owner question 2026-06-13",
        "",
        "Original B747: 'calibrate the survivor-bias direction'.",
        "Owner pushback: *'why does there need to be any delisting?'*",
        "Re-scoped finding: T1a ALREADY tracks 111 historical-removed names; the",
        "question is whether every engine honors the PIT universe per-bar or",
        "collapses to the END-snapshot.",
        "",
        "## T1a roster composition",
        "",
        f"- Total rows in T1a: **{rep.t1a_total}**",
        f"- Currently active (never removed): **{rep.t1a_active}**",
        f"- Historical-removed during window: **{rep.t1a_historical_removed}**",
        "",
        "## OHLCV coverage for historical-removed tickers",
        "",
        f"- OHLCV parquet present: **{rep.ohlcv_present_for_removed}** of {rep.t1a_historical_removed}",
        f"- OHLCV parquet MISSING: **{len(rep.ohlcv_missing_for_removed)}**",
    ]
    if rep.ohlcv_missing_for_removed:
        L.append(f"  - missing names: `{', '.join(rep.ohlcv_missing_for_removed)}`")
        L.append("  - These names CANNOT be simulated even if the PIT filter were fixed; coverage gap is independent.")
    L.extend([
        "",
        "### Coverage-through-removal verification",
        "",
        "For each historical-removed ticker with OHLCV present, does the parquet contain bars through the removal date (within 1 trading day)?",
        "",
    ])
    n_through = sum(1 for h in rep.historical_tickers if h.coverage_through_removal)
    n_short = sum(1 for h in rep.historical_tickers if h.ohlcv_exists and not h.coverage_through_removal)
    L.extend([
        f"- Coverage through removal date: **{n_through}** tickers",
        f"- OHLCV present but ENDS before removal date: **{n_short}** tickers (data gap)",
        "",
    ])
    short_list = [h for h in rep.historical_tickers if h.ohlcv_exists and not h.coverage_through_removal]
    if short_list:
        L.append("Tickers with truncated OHLCV (last bar before removal date):")
        L.append("")
        for h in short_list[:10]:
            L.append(f"- `{h.symbol}` -- last bar {h.ohlcv_last_bar}, removed {h.removed_date}")
        if len(short_list) > 10:
            L.append(f"- ... and {len(short_list) - 10} more")
        L.append("")

    L.extend([
        "## Consumer PIT-discipline verdict",
        "",
        "| Consumer | Pattern | Verdict | Note |",
        "|---|---|---|---|",
    ])
    for c in rep.consumers:
        L.append(f"| `{c.consumer}` | {c.universe_load_pattern} | **{c.verdict}** | {c.note} |")
    L.extend([
        "",
        "## Headline finding",
        "",
    ])
    n_incorrect = sum(1 for c in rep.consumers if c.verdict == "PIT_INCORRECT")
    if n_incorrect == 0:
        L.append("**All audited consumers respect the PIT universe.** Survivor bias not introduced by universe-load logic; verify other vectors (e.g., delisted-ticker OHLCV ends BEFORE removal date is a data-quality issue, not a survivor-bias issue).")
    else:
        L.append(f"**{n_incorrect} consumer(s) load the universe with PIT filter applied at END date instead of per-bar.** This silently excludes the {rep.t1a_historical_removed} historical-removed tickers from every measurement, introducing END-snapshot survivor bias.")
        L.append("")
        L.append(f"**Estimated (ticker, bar) cells silently excluded by measure_fire_count.py over the {start} -> {end} window: ~{rep.estimated_excluded_ticker_bars:,}**")
        L.append("")
        L.append("Bias direction:")
        L.append("- Fires/year/strategy is computed from `n_fires_long / calendar_year_span`; excluded ticker-bars => lower numerator => UNDER-estimates fire rate.")
        L.append("- But the per-strategy WR / Sharpe / ROI verdicts derived from the cube REPLAY (Stage 5) inherit the same survivorship in the OPPOSITE direction: the strategies that delisted ARE the failing ones, so OVER-estimates per-strategy WR (the classic survivor-bias direction).")
        L.append("- Net: fire-counts under-bias; WR/Sharpe over-bias. Both inherit the same fix.")
    L.extend([
        "",
        "## Owner action items",
        "",
        "1. Re-confirm whether `measure_fire_count.py` should switch to per-bar PIT (more expensive; honest) or stay end-date (current behavior; surveys-currently-listed only).",
        "2. Investigate the OHLCV coverage gaps for historical-removed tickers; backfill via Polygon Tickers API or accept as known gap.",
        "3. Decide whether B690b AWS measurement re-run should be GATED on the fix landing, or proceed with current END-snapshot scope + apply the bias adjustment factor offline.",
    ])
    return "\n".join(L)


def main():
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2020-01-01")
    p.add_argument("--end",   default="2026-05-31")
    p.add_argument("--md", default=str(OUT_DIR / "b747_audit_report.md"))
    p.add_argument("--json", default=str(OUT_DIR / "b747_audit_results.json"))
    args = p.parse_args()
    start = date.fromisoformat(args.start)
    end   = date.fromisoformat(args.end)

    print(f"[B747] PIT-discipline audit window {start} -> {end}")
    rep = audit_pit_discipline(start, end)
    md = render_report(rep, start, end)
    Path(args.md).write_text(md, encoding="utf-8")
    json_payload = {
        "t1a_total": rep.t1a_total,
        "t1a_active": rep.t1a_active,
        "t1a_historical_removed": rep.t1a_historical_removed,
        "ohlcv_present_for_removed": rep.ohlcv_present_for_removed,
        "ohlcv_missing_for_removed": rep.ohlcv_missing_for_removed,
        "estimated_excluded_ticker_bars": rep.estimated_excluded_ticker_bars,
        "consumers": [
            {"consumer": c.consumer, "pattern": c.universe_load_pattern,
             "verdict": c.verdict, "note": c.note}
            for c in rep.consumers
        ],
        "historical_tickers": [
            {"symbol": h.symbol, "removed_date": str(h.removed_date),
             "ohlcv_exists": h.ohlcv_exists, "ohlcv_n_bars": h.ohlcv_n_bars,
             "ohlcv_first_bar": str(h.ohlcv_first_bar) if h.ohlcv_first_bar else None,
             "ohlcv_last_bar":  str(h.ohlcv_last_bar)  if h.ohlcv_last_bar  else None,
             "coverage_through_removal": h.coverage_through_removal}
            for h in rep.historical_tickers
        ],
    }
    Path(args.json).write_text(json.dumps(json_payload, indent=2), encoding="utf-8")
    print(f"[B747] T1a: total={rep.t1a_total}  active={rep.t1a_active}  historical-removed={rep.t1a_historical_removed}")
    print(f"[B747] OHLCV present for removed: {rep.ohlcv_present_for_removed} / {rep.t1a_historical_removed}")
    if rep.ohlcv_missing_for_removed:
        print(f"[B747] OHLCV MISSING: {rep.ohlcv_missing_for_removed}")
    print(f"[B747] Consumer verdicts:")
    for c in rep.consumers:
        print(f"         {c.consumer:42s}  {c.verdict:14s}  {c.universe_load_pattern}")
    print(f"[B747] Estimated excluded (ticker, bar) cells: {rep.estimated_excluded_ticker_bars:,}")
    print(f"[B747] WROTE {args.md}")
    print(f"[B747] WROTE {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
