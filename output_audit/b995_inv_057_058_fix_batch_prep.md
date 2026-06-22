# B995 — INV-057 + INV-058 Fix Batch Readiness Package

**Status:** DOC-ONLY-PREP (pending S5-EARNINGS-BLACKOUT-LOOKAHEAD-FIX-BATCH owner approval)

**Source:** Council 99 5-turn standing approval T3/5 + Council 94 B989 walk-2 honest-finding pivot + B989 EXECUTION_QUEUE ticket S5-EARNINGS-BLACKOUT-LOOKAHEAD-FIX-BATCH.

**Purpose:** Pre-flight ready-to-execute plan for owner approval to ship dedicated INV-057+058 fix batch. Doc-only this turn; no code changes. Plan finalizes (1) exact diff sites, (2) test scaffold, (3) cube re-measurement protocol, (4) Phase 1B-α gating exclusion lift criteria.

---

## INV-057 — `as_of` not passed to `fetch_earnings_dates`

**Root cause:** `backtest/engine/exit_strategies.py:507` calls `fetch_earnings_dates(ticker)` without `as_of` parameter. `backtest/data/fetcher.py:236-263` signature is `fetch_earnings_dates(ticker, as_of=None)`. When `as_of=None`, line 257-258 (`if as_of:`) skips the PIT filter and returns the FULL earnings calendar 2020-2026.

**Bias direction:** POSITIVE lookahead (knows future scheduled earnings at backtest time).

**Fix diff (proposed):**

```python
# backtest/engine/exit_strategies.py line 504-515 (current):
    if earnings_dates is None and ticker:
        try:
            from backtest.data.fetcher import fetch_earnings_dates
            df_e = fetch_earnings_dates(ticker)
            if df_e is not None and not df_e.empty:
                earnings_dates = pd.to_datetime(
                    df_e["earnings_date"]
                ).dt.date.tolist()
        except Exception as exc:
            logger.debug("exit_earnings_blackout: earnings fetch failed (%s): %s",
                          ticker, exc)
            earnings_dates = []

# B996 fix (proposed):
    if earnings_dates is None and ticker:
        try:
            from backtest.data.fetcher import fetch_earnings_dates
            # INV-057 fix: pass as_of=entry_date for PIT compliance.
            # Filters earnings calendar to dates known at backtest entry,
            # preventing positive lookahead bias from future earnings
            # dates scheduled later than entry_date.
            df_e = fetch_earnings_dates(ticker, as_of=entry_date)
            if df_e is not None and not df_e.empty:
                earnings_dates = pd.to_datetime(
                    df_e["earnings_date"]
                ).dt.date.tolist()
        except Exception as exc:
            logger.debug("exit_earnings_blackout: earnings fetch failed (%s): %s",
                          ticker, exc)
            earnings_dates = []
```

**Diff size:** 2-line change (add `as_of=entry_date` kwarg + 4-line rationale comment).

---

## INV-058 — `filing_date` ≠ `earnings_announce_date` semantic gap

**Root cause:** `backtest/data/fetcher.py:255` derives earnings dates via `df["earnings_date"] = pd.to_datetime(df["filing_date"])`. Polygon financials `filing_date` is the 10-Q/10-K filing date — which occurs ~1-30 days AFTER the actual earnings announcement.

**Bias direction:** Late exit relative to actual earnings announcement. Strategy holds through the earnings event and exits ~1-30 days later.

**Fix options (per B989 EXECUTION_QUEUE ticket):**

**Option (a) — separate `earnings_announce_date` field investigation:**
Check if Polygon financials parquet exposes a separate announce-date field beyond `filing_date`. Specifically inspect column inventory of `data_prefetch/polygon/financials/{TICKER}.parquet`. If field exists, swap to it.

**Option (b) — apply -30 trading days proxy:**
If only `filing_date` available, shift exit target by -30 trading days as approximation of actual announce date. Document the proxy explicitly.

**Option (c) — Finnhub earnings endpoint:**
Existing `data_prefetch/finnhub/earnings/` may provide actual announce dates. Cross-reference.

**Pre-flight investigation required (in B996 fix batch):**

```python
# Inspect Polygon financials schema
import pandas as pd
from pathlib import Path
df = pd.read_parquet("data_prefetch/polygon/financials/AAPL.parquet")
print("Columns:", list(df.columns))
# Look for: announce_date, earnings_release_date, report_date, 
# date_filed, period_of_report, etc.
```

**B998 (2026-06-22 Council 100 T1/5) RESULT: Polygon parquet does NOT have `announce_date` or `earnings_release_date` column.**

Available date columns: `filing_date`, `end_date`, `period_of_report_date` (often NULL), `start_date`. Across 8 sampled tickers (AAPL/MSFT/GOOGL/AMZN/TSLA/JPM/WMT/JNJ): filing_date - end_date gap = 26-40 days (mean ~32, median ~32). Total files: 1,937.

**Option-a (column swap) NOT VIABLE.** B996 fix must use Option-b (proxy) or Option-c (Finnhub). T2 (B999) Finnhub investigation will determine final scope.

**B998 finding refines B996 fix scope:**
- IF Finnhub provides `announce_date` (B999 T2 result) → Option-c; INV-058 fix becomes data-source swap (clean)
- ELSE → Option-b; INV-058 fix uses `end_date + 30 days` proxy (more stable than `filing_date - 30 days` since end_date is fiscal-calendar-known)

**B999 (2026-06-22 Council 100 T2/5) RESULT: Finnhub `/stock/earnings` endpoint does NOT provide `announce_date` either.**

Finnhub schema (data_prefetch/finnhub/earnings/*.parquet; 1,938 files): canonical columns = `actual, estimate, period, quarter, surprise, surprisePercent, symbol, year`. The `period` field is the fiscal-period-end-date (e.g., AAPL 2026-03-31 for Q2 2026) — same semantics as Polygon `end_date`. NO native `announce_date` field.

**Option-c (Finnhub fallback) ALSO NOT VIABLE per local cache constraints.**

**B996 INV-058 fix scope finalized: Option-d (`end_date + 30 days` proxy).** Cleanest implementation; works with both Polygon and Finnhub; matches empirical filing-gap median (~32 days across 8 sampled tickers). Honest acknowledgment in producer docstring that this is a proxy approximation of actual earnings-announce-date.

**Updated fix diff (Option-c conditional on Finnhub availability):**

```python
# backtest/data/fetcher.py (proposed B996 with Finnhub source):
def fetch_earnings_dates(ticker, as_of=None):
    """B996 INV-058 fix: prefer Finnhub announce_date if available,
    else fall back to Polygon end_date + 30 days proxy (B998 verified
    no native announce_date column in Polygon financials parquet).
    """
    # Try Finnhub first (cleanest source per B999 T2 verification)
    finnhub_path = Path(...) / "data_prefetch/finnhub/earnings" / f"{ticker}.parquet"
    if finnhub_path.exists():
        df = pd.read_parquet(finnhub_path)
        if "announce_date" in df.columns:
            df["earnings_date"] = pd.to_datetime(df["announce_date"])
            # ... PIT filter + return
    # Fallback: Polygon end_date + 30 days
    polygon_path = Path(...) / "data_prefetch/polygon/financials" / f"{ticker}.parquet"
    df = pd.read_parquet(polygon_path)
    df["earnings_date"] = pd.to_datetime(df["end_date"]) + pd.Timedelta(days=30)
    # ... PIT filter + return
```

Decision tree:
- IF Polygon has separate `announce_date` column → Option (a); swap `filing_date` → `announce_date`
- ELIF Finnhub earnings provides per-ticker announce dates → Option (c); pivot data source
- ELSE → Option (b); apply -30-trading-day shift with explicit proxy documentation

**Fix diff (Option a, conditional on field existence):**

```python
# backtest/data/fetcher.py line 252-259 (current):
    try:
        df = pd.read_parquet(fin_path)
        if df.empty or "filing_date" not in df.columns:
            return pd.DataFrame()
        df["earnings_date"] = pd.to_datetime(df["filing_date"])
        df = df.dropna(subset=["earnings_date"])
        if as_of:
            df = df[df["earnings_date"].dt.date <= as_of]
        return df[["earnings_date"]].drop_duplicates().sort_values("earnings_date")

# B996 fix Option (a) (proposed):
    try:
        df = pd.read_parquet(fin_path)
        if df.empty:
            return pd.DataFrame()
        # INV-058 fix: prefer announce_date over filing_date.
        # filing_date is the 10-Q/10-K filing (~1-30 days AFTER actual
        # earnings announce). For blackout-exit timing we want the
        # announce-date proxy. Order of preference:
        #   announce_date > earnings_release_date > period_of_report
        #   > filing_date - 30 trading days fallback.
        if "announce_date" in df.columns:
            df["earnings_date"] = pd.to_datetime(df["announce_date"])
        elif "earnings_release_date" in df.columns:
            df["earnings_date"] = pd.to_datetime(df["earnings_release_date"])
        elif "filing_date" in df.columns:
            # Fallback proxy: filing_date - 30 trading days approximates
            # announce date (Polygon publishes filings AFTER earnings call).
            df["earnings_date"] = pd.to_datetime(df["filing_date"]) - pd.tseries.offsets.BDay(30)
        else:
            return pd.DataFrame()
        df = df.dropna(subset=["earnings_date"])
        if as_of:
            df = df[df["earnings_date"].dt.date <= as_of]
        return df[["earnings_date"]].drop_duplicates().sort_values("earnings_date")
```

**Diff size:** ~10 lines (column prefer-list + proxy fallback + comment block).

---

## New unit tests required (B996 fix batch)

### `backtest/tests/test_b996_inv_057_058_earnings_blackout_pit.py`

```python
"""B996: INV-057 + INV-058 earnings_blackout lookahead fix verification."""
from datetime import date
import pandas as pd
from backtest.engine.exit_strategies import exit_earnings_blackout
from backtest.data.fetcher import fetch_earnings_dates


def test_b996_fetch_earnings_dates_respects_as_of():
    """INV-057: fetch_earnings_dates with as_of filters PIT-correctly."""
    # Use a known ticker with multiple earnings dates
    full = fetch_earnings_dates("AAPL")  # no as_of -> full calendar
    pit_2022 = fetch_earnings_dates("AAPL", as_of=date(2022, 1, 1))
    # PIT must be subset of full
    assert len(pit_2022) < len(full), (
        f"PIT filter must reduce calendar; full={len(full)} pit={len(pit_2022)}"
    )
    # No date in PIT result should be after as_of
    if not pit_2022.empty:
        max_pit = pit_2022["earnings_date"].max().date()
        assert max_pit <= date(2022, 1, 1), (
            f"PIT must respect as_of cutoff; got max={max_pit}"
        )


def test_b996_exit_earnings_blackout_calls_fetch_with_as_of():
    """INV-057: exit_earnings_blackout must pass entry_date as as_of."""
    # Source-grep verification: exit_strategies.py:~507 must contain
    # `fetch_earnings_dates(ticker, as_of=entry_date)` or equivalent
    src = open("backtest/engine/exit_strategies.py").read()
    assert "fetch_earnings_dates(ticker, as_of=entry_date)" in src or \
           "fetch_earnings_dates(\n            ticker, as_of=entry_date" in src, \
        "exit_earnings_blackout must pass as_of=entry_date to fetch_earnings_dates"


def test_b996_announce_date_preferred_over_filing_date():
    """INV-058: fetcher prefers announce_date column when available."""
    # If Polygon parquet has announce_date column, use it
    # Test via synthetic DataFrame with both columns
    import tempfile, os
    df = pd.DataFrame({
        "filing_date": ["2024-01-25"],  # 25 days after announce
        "announce_date": ["2024-01-01"],
    })
    # Verify fetcher logic prefers announce_date
    # (implementation-specific test; will be filled when fix lands)
    pass  # placeholder; concrete test in B996 ship


def test_b996_pre_announce_date_shift_proxy():
    """INV-058: -30 BDay proxy when announce_date absent."""
    # Verify filing_date - 30 BDay approximates announce timing
    filing = pd.Timestamp("2024-02-15")  # typical Q4 10-K filing
    shifted = filing - pd.tseries.offsets.BDay(30)
    # ~30 business days back from mid-Feb = early Jan
    assert shifted.month == 1 and shifted.year == 2024
```

---

## Cube re-measurement protocol

**Scope:** All R4/R5 cube cells where exit_method == "earnings_blackout".

**Identification:**
```python
# scripts/b996_identify_affected_cube_cells.py (proposed)
import pandas as pd
df = pd.read_parquet("output_batch395_final/trade_exit_detail.csv")
affected_cells = df[df["exit_method"] == "earnings_blackout"].groupby(
    ["strategy", "exit_method"]
).agg(
    n_trades=("entry_date", "count"),
    total_pnl_pct=("pnl_pct", "sum"),
).reset_index()
print(f"Affected cells: {len(affected_cells)}")
affected_cells.to_json("output_audit/b996_affected_earnings_blackout_cells.json", orient="records", indent=2)
```

**Re-run protocol:**
1. Apply INV-057+058 fixes (B996 ship)
2. Pyramid GREEN baseline
3. Re-run R4 cube with fixed `exit_earnings_blackout` (~hours scope per CHECKLIST #13 expensive-job protocol; owner approves first)
4. Diff per-cell PnL_pct: pre-fix vs post-fix
5. Annotate cells where ΔPnL > 50% as "lookahead-corrected"
6. B981 walk-2 5 strategies (bollinger_tight + break_retest_volume + bullish_engulfing_support + cmf_flip + double_bottom_long) get post-fix cube measurements

**Owner approval gates (per CHECKLIST #13/#22/#23/#29 expensive-job protocol):**
- Pre-cube-re-run: small test batch (1 strategy × earnings_blackout) → manual review
- Owner approval → scale to full re-measurement
- Result manifest review → owner approval → cube state transition

---

## Phase 1B-α gating exclusion lift criteria

Per B989 walk-2 disposition + B994 banner item (v) verification: earnings_blackout cube cells are currently EXCLUDED from Phase 1B-α gating subset pending INV-057+058 closure.

**Lift criteria (post-B996 ship):**
1. Both INV-057 + INV-058 fixes shipped + pyramid GREEN
2. Cube re-measurement complete on affected cells
3. Per-cell ΔPnL documented in `output_audit/b996_cube_remeasurement_diff.json`
4. Owner approval to lift exclusion

**Closure mechanism:**
- INV-057 status: OPEN → RESOLVED-IMPLEMENTED-B996
- INV-058 status: OPEN → RESOLVED-IMPLEMENTED-B996
- B981 walk-2 5 strategies disposition: DEFERRED-FIXED-IN-INV-057+058 → CUBE-RE-MEASURED-POST-B996
- Phase 1B-α gating exclusion: LIFTED

---

## B996 readiness summary

| Item | Status |
|---|---|
| INV-057 fix diff | ✅ Drafted (2-line change + comment) |
| INV-058 fix diff | ✅ Drafted (Option-a with column prefer-list + proxy fallback) |
| Unit test scaffold | ✅ Drafted (4 tests in test_b996_inv_057_058_earnings_blackout_pit.py) |
| Cube re-measurement protocol | ✅ Drafted (identification script + diff protocol + owner gate) |
| Phase 1B-α exclusion lift criteria | ✅ Drafted (4 criteria) |
| Pre-flight Polygon schema check | ⏳ TODO at B996 ship (announce_date column existence) |
| Pre-flight Finnhub fallback check | ⏳ TODO at B996 ship (Option-c availability) |

**B996 estimated scope:**
- Code: ~12 lines changed (exit_strategies.py:507 + fetcher.py:252-259)
- Tests: 4 new unit tests (~80 LOC)
- Cube re-run: hours-scope per CHECKLIST #13 (owner-approved)
- Documentation: doc-sync + EXECUTION_QUEUE + CLAUDE.md + INV-057+058 status update

**B996 owner-pre-approval-gated** per B989 EXECUTION_QUEUE ticket designation. This B995 doc-only prep packages the work for clean owner approval; B996 ships on explicit owner directive.

---

**Memory rule cross-references:**
- `feedback_audit_recommendations_against_existing_directives` (B989 explicit gating)
- `feedback_narrow_scope_blast_radius` (infra-fix at exit-method level)
- `feedback_sequence_or_split_when_stacking_changes` (INV-057+058 bundled for clean attribution)
- `feedback_local_changes_default_global_needs_approval` (infrastructure-change flagged)
- CHECKLIST #13 / #22 / #23 / #29 (expensive-job protocol applies to cube re-run)
- CHECKLIST #114 STOP CONDITIONS (schema-change discipline; DEC needed pre-ship)
- Council 76 banner-verification + Council 94 honest-finding pivot precedents

**Ship trigger:** owner explicit directive on S5-EARNINGS-BLACKOUT-LOOKAHEAD-FIX-BATCH.
