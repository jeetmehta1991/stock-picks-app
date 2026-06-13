# Source: B690 revised step 1 + owner critique pull-forward + Decision 5 Cat 1 per CHECKLIST #77
"""B745 finding-grade producer audit for TIER 2 producers.

PER OWNER CRITIQUE 2026-06-13: this is NOT just engineering classification.
It is a finding-grade output. The two stub producers (per B689 framing,
patentmomentum + corporatedonors) need a strategy-level dead-strategy
determination: if a strategy's distinguishing signal has been `{}` for
months, it has been firing on its other gates only -- same orphan-emitter
class as SM-5 + SMC vendored-library SPOF.

INVESTIGATION FINDING (PRE-AUDIT) 2026-06-13: B689's "STUB caches (1 entry
each)" claim is FALSE. Direct probe of the parquets shows:
  - patentmomentum/global.parquet: 5,830,800 rows (5.8M, 6.9MB)
  - corporatedonors/global.parquet: 25,000 rows across 432 unique tickers
This means the original "silent-gap risk" framing inverts: the data IS
present, but the audit must confirm the producers READ + EMIT it correctly
AND that consuming strategies actually fire.

The 16 TIER 2 producers are classified into 4 paths:
  Path A -- has module-level per-ticker cache; call as-is in measure_fire_count.py
  Path B -- needs module-level cache added (unlikely after B316b/B421/B535/B528/B534)
  Path C -- needs ohlcv_dict or full-universe data (cross_sectional)
  Path D -- producer reads stub-or-corrupt cache; consuming strategies effectively dead

For each producer the audit answers:
  1. What is the producer's caching mechanism (module dict, lru_cache, none)?
  2. What is the underlying cache file's row count + ticker coverage?
  3. Does the producer emit a non-empty dict on a smoke probe?
  4. (Path D only) Which strategies in screener.py consume the emitted keys,
     and have they been effectively dead?

USAGE
-----
    python scripts/audit_tier2_producer_caches.py
    python scripts/audit_tier2_producer_caches.py --json output_audit/b745_audit.json

OUTPUT
------
    output_audit/b745_tier2_producer_audit/b745_audit_report.md
    output_audit/b745_tier2_producer_audit/b745_audit_results.json
"""
from __future__ import annotations

import importlib
import json
import re
import sys
import traceback
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))

OUT_DIR = _REPO / "output_audit" / "b745_tier2_producer_audit"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SCREENER_PATH = _REPO / "backtest" / "signals" / "screener.py"
DATA_PREFETCH = _REPO / "data_prefetch"


# --------------------------------------------------------------------------
# Registry of 16 TIER 2 producers + their data sources
# --------------------------------------------------------------------------
@dataclass
class ProducerSpec:
    module: str
    func: str
    cache_var: str = ""        # module-level cache variable name to detect
    data_path: str = ""        # parquet path or dir to probe
    consumed_signal_keys: tuple = ()  # emitted-key names consumers may grep for

PRODUCERS: list[ProducerSpec] = [
    ProducerSpec("backtest.signals.insider_buying", "compute_insider_cluster_signals",
                 cache_var="_INSIDERS_BY_TICKER",
                 data_path="data_prefetch/quiver/insiders/global.parquet",
                 consumed_signal_keys=("insider_cluster_active", "insider_unique_buyers_30d")),
    ProducerSpec("backtest.signals.institutional_persistence_consumer", "compute_persistence_signals",
                 cache_var="_CACHE",
                 data_path="data_prefetch/quiver/sec13fchanges",
                 consumed_signal_keys=("institutional_persistence_5q", "institutional_persistence_3q")),
    ProducerSpec("backtest.signals.short_interest", "compute_short_interest_signals",
                 cache_var="_SI_BY_TICKER",
                 data_path="data_prefetch/finra/short_interest",
                 consumed_signal_keys=("short_interest_pct", "days_to_cover")),
    ProducerSpec("backtest.signals.sec_edgar_extractor", "compute_sec_edgar_signals",
                 cache_var="_DECODED_DF_CACHE",
                 data_path="data_prefetch/sec_edgar",
                 consumed_signal_keys=("sec_edgar_8k_recent",)),
    ProducerSpec("backtest.signals.news_sentiment", "compute_news_sentiment_signals",
                 cache_var="_NEWS_BY_TICKER",
                 data_path="data_prefetch/quiver/quivernews",
                 consumed_signal_keys=("news_sentiment_score_1d", "news_sentiment_score_7d")),
    ProducerSpec("backtest.signals.pead", "compute_pead_signals",
                 cache_var="load_quarterly_eps",  # via @lru_cache
                 data_path="data_prefetch/polygon/financials",
                 consumed_signal_keys=("within_pead_window", "days_since_last_earnings")),
    ProducerSpec("backtest.signals.earnings_surprise_yoy", "compute_yoy_surprise_signal",
                 cache_var="",  # inherits PEAD's lru_cache
                 data_path="data_prefetch/polygon/financials",
                 consumed_signal_keys=("earnings_eps_yoy_growth",)),
    ProducerSpec("backtest.signals.search_volume", "compute_search_volume_signals",
                 cache_var="_PYTRENDS_BY_TICKER",
                 data_path="data_prefetch/pytrends",
                 consumed_signal_keys=("search_volume_spike",)),
    ProducerSpec("backtest.signals.index_rebalance", "compute_index_rebalance_signals",
                 cache_var="",  # _load_events() uses module-level scope check
                 data_path="Backtesting universe/index_rebalance_events.parquet",
                 consumed_signal_keys=("index_rebalance_window",)),
    # compute_recent_8k_signal DELETED in B748b 2026-06-13 (genuine orphan:
    # 0 consumers in ALL_STRATEGIES, 0 data rows). Registry size 17 -> 16.
    ProducerSpec("backtest.signals.congressional_alt_data", "compute_housetrading_signals",
                 cache_var="_HOUSETRADING_BY_TICKER",
                 data_path="data_prefetch/quiver/housetrading",
                 consumed_signal_keys=("housetrading_recent", "congressional_buyer_recent")),
    ProducerSpec("backtest.signals.congressional_alt_data", "compute_gov_contracts_signals",
                 cache_var="_GOV_CONTRACTS_BY_TICKER",
                 data_path="data_prefetch/quiver/gov_contracts",
                 consumed_signal_keys=("gov_contracts_recent",)),
    ProducerSpec("backtest.signals.congressional_alt_data", "compute_lobbying_signals",
                 cache_var="_LOBBYING_BY_TICKER",
                 data_path="data_prefetch/quiver/lobbying",
                 consumed_signal_keys=("lobbying_recent",)),
    ProducerSpec("backtest.signals.congressional_alt_data", "compute_patentmomentum_signals",
                 cache_var="_PATENT_BY_TICKER",
                 data_path="data_prefetch/quiver/patentmomentum/global.parquet",
                 consumed_signal_keys=("patent_momentum_recent", "patent_momentum_above_avg")),
    ProducerSpec("backtest.signals.congressional_alt_data", "compute_offexchange_signals",
                 cache_var="_OFFEXCHANGE_BY_TICKER",
                 data_path="data_prefetch/quiver/offexchange",
                 consumed_signal_keys=("dpi_recent", "dpi_elevated", "otc_short_ratio_recent")),
    ProducerSpec("backtest.signals.congressional_alt_data", "compute_corporatedonors_signals",
                 cache_var="_DONORS_BY_TICKER",
                 data_path="data_prefetch/quiver/corporatedonors/global.parquet",
                 consumed_signal_keys=("corporate_donors_recent", "corporate_donor_aligned")),
    ProducerSpec("backtest.signals.cross_sectional", "compute_cross_sectional_features",
                 cache_var="_FINANCIALS_BY_TICKER",
                 data_path="data_prefetch/polygon/financials",
                 consumed_signal_keys=("xs_momentum_top_decile", "xs_momentum_bottom_decile")),
]


# --------------------------------------------------------------------------
# Per-producer audit
# --------------------------------------------------------------------------
@dataclass
class ProducerAuditRow:
    producer: str
    module: str
    cache_var: str
    cache_mechanism: str        # "module_dict" | "lru_cache" | "none" | "needs_ohlcv_dict"
    path_classification: str    # "A" | "B" | "C" | "D"
    data_path: str
    data_exists: bool
    data_row_count: int
    data_unique_tickers: int
    smoke_emits_non_empty: bool
    smoke_signal_keys: list = field(default_factory=list)
    smoke_error: str = ""
    consumed_signal_keys: list = field(default_factory=list)
    consuming_strategies: list = field(default_factory=list)
    # B748d per CHECKLIST #106 -- new probes
    producer_source_path: str = ""        # (a) discovered from producer source
    temporal_coverage: dict = field(default_factory=dict)  # (c)
    schema_contract: dict = field(default_factory=dict)    # (d)
    issue_flags: list = field(default_factory=list)        # human-readable verdicts
    notes: str = ""


def _probe_data_path(path_str: str) -> tuple[bool, int, int]:
    """B748d (2026-06-14) per CHECKLIST #106(b): RECURSIVE glob, not parent-only.

    Returns (exists, row_count, unique_tickers).

    For a single parquet file: counts rows + unique Ticker (case-insensitive).
    For a directory of per-ticker parquets: recursive scan (**/*.parquet) so
    nested subdir layouts (e.g. SEC EDGAR `<form>/<TICKER>.parquet`) are
    discovered. Pre-B748d this used parent-only glob and missed 11 form-type
    subdirs × ~1700 files each in `data_prefetch/sec_edgar/`.
    """
    path = _REPO / path_str
    if not path.exists():
        return (False, 0, 0)
    try:
        import pandas as pd
        if path.is_file() and path.suffix == ".parquet":
            df = pd.read_parquet(path)
            n_rows = len(df)
            n_tickers = 0
            for col in ("Ticker", "ticker", "TICKER"):
                if col in df.columns:
                    n_tickers = int(df[col].nunique())
                    break
            return (True, n_rows, n_tickers)
        if path.is_dir():
            # B748d: recursive glob to catch nested subdirs (per CHECKLIST #106(b))
            parquets = list(path.rglob("*.parquet"))
            n_rows = 0
            for p in parquets[:50]:  # cap at 50 files for speed
                try:
                    n_rows += len(pd.read_parquet(p))
                except Exception:
                    pass
            return (True, n_rows, len(parquets))
        return (True, 0, 0)
    except Exception:
        return (True, 0, 0)


def _discover_producer_path(spec: "ProducerSpec") -> str:
    """B748d per CHECKLIST #106(a): identify producer's TRUE cache path by
    READING THE PRODUCER FUNCTION SOURCE (not just any module-level constant).

    ALWAYS runs (B748d revision: prior version skipped discovery when the
    registry path also existed, missing the case where both paths exist
    but point to DIFFERENT data -- e.g. `compute_sec_edgar_signals` whose
    registry points to `sec_edgar/` raw filing-index while the producer
    actually reads `sec_edgar_decoded/` with the enriched `item_codes`
    column. Caller compares against `spec.data_path` to decide drift).

    Parses the producer function body to find module-level path constants
    referenced inside it + walks called helpers in the same module to
    catch orchestrator producers (e.g. compute_sec_edgar_signals calls
    sc_13d_filed_within_days + eight_k_item_filed_within_days which use
    _DECODED_CACHE_DIR).
    """
    try:
        mod = importlib.import_module(spec.module)
        full_src = Path(mod.__file__).read_text(encoding="utf-8")
    except Exception:
        return ""
    # Find function body
    func_pat = re.compile(rf'^def {re.escape(spec.func)}\b', re.MULTILINE)
    m = func_pat.search(full_src)
    if not m:
        return ""
    start = m.start()
    next_def = re.search(r"^def \w+", full_src[start + 1:], re.MULTILINE)
    end = start + 1 + next_def.start() if next_def else len(full_src)
    body = full_src[start:end]
    # B748d: walk same-module helpers transitively (BFS to depth 3) so we
    # catch orchestrator -> helper -> _load function chains (e.g. sec_edgar
    # compute -> sc_13d_filed_within_days -> _load_decoded -> _DECODED_CACHE_DIR)
    bodies_to_scan = [body]
    seen: set[str] = {spec.func}
    frontier = [body]
    skip_calls = {"isinstance", "len", "str", "int", "float", "bool", "dict",
                  "set", "list", "tuple", "print", "round", "min", "max",
                  "sum", "any", "all", "pd", "np", "Path", "open", "type",
                  "range", "zip", "map", "filter", "sorted", "reversed",
                  "getattr", "hasattr", "setattr", "iter", "next", "enumerate",
                  "update", "get", "items", "keys", "values", "copy", "append"}
    for _depth in range(3):
        new_frontier = []
        for b in frontier:
            helper_calls = set(re.findall(r"\b([a-z_][a-z0-9_]*)\(", b))
            for h in helper_calls:
                if h in skip_calls or h in seen:
                    continue
                h_pat = re.compile(rf'^def {re.escape(h)}\b', re.MULTILINE)
                hm = h_pat.search(full_src)
                if hm:
                    h_start = hm.start()
                    h_next = re.search(r"^def \w+", full_src[h_start + 1:], re.MULTILINE)
                    h_end = h_start + 1 + h_next.start() if h_next else len(full_src)
                    h_body = full_src[h_start:h_end]
                    bodies_to_scan.append(h_body)
                    new_frontier.append(h_body)
                    seen.add(h)
        frontier = new_frontier
        if not frontier:
            break
    used_constants: set[str] = set()
    for b in bodies_to_scan:
        used_constants.update(re.findall(r"\b(_[A-Z][A-Z0-9_]*)\b", b))
    candidates = []
    for attr_name in used_constants:
        val = getattr(mod, attr_name, None)
        if isinstance(val, Path):
            candidates.append((attr_name, val))
    if not candidates:
        return ""
    # Prefer the candidate whose path exists
    for name, p in candidates:
        if p.exists():
            try:
                return str(p.relative_to(_REPO))
            except ValueError:
                return str(p)
    return ""


def _temporal_coverage_probe(path_str: str,
                              window_start: str = "2020-01-01",
                              window_end: str = "2026-05-31",
                              date_cols: tuple = ("filing_date", "Date", "date",
                                                    "TransactionDate", "event_date",
                                                    "settlement_date")) -> dict:
    """B748d per CHECKLIST #106(c): temporal coverage probe.

    Returns dict with:
      first_date, last_date: actual date range in the data
      window_start, window_end: requested measurement window
      covers_start, covers_end: bool flags
      gap_days_at_start, gap_days_at_end: int (negative = ahead, positive = stale)
    Aggregates across all parquets in a directory (recursive) or reads the
    single parquet.
    """
    path = _REPO / path_str
    if not path.exists():
        return {"present": False}
    try:
        import pandas as pd
        all_dates: list = []
        if path.is_file() and path.suffix == ".parquet":
            df = pd.read_parquet(path)
            for c in date_cols:
                if c in df.columns:
                    dt = pd.to_datetime(df[c], errors="coerce").dropna()
                    all_dates.extend(dt.tolist())
                    break
        elif path.is_dir():
            files = list(path.rglob("*.parquet"))
            # Sample stratified: first + last + middle + 7 random per CHECKLIST #11
            # (granular before aggregating)
            sample = files[:5] + files[-5:] + files[len(files)//2 : len(files)//2 + 5] if len(files) > 15 else files
            sample = list(dict.fromkeys(sample))[:20]
            for f in sample:
                try:
                    df = pd.read_parquet(f)
                    for c in date_cols:
                        if c in df.columns:
                            dt = pd.to_datetime(df[c], errors="coerce").dropna()
                            all_dates.extend(dt.tolist())
                            break
                except Exception:
                    pass
        if not all_dates:
            return {"present": True, "no_date_col": True}
        first = min(all_dates).date()
        last = max(all_dates).date()
        ws = date.fromisoformat(window_start)
        we = date.fromisoformat(window_end)
        return {
            "present": True,
            "first_date": str(first),
            "last_date": str(last),
            "covers_window_start": first <= ws,
            "covers_window_end": last >= we,
            "gap_days_at_start": (first - ws).days,
            "gap_days_at_end": (we - last).days,
            "is_stale": (we - last).days > 90,
            "is_narrow_window": (last - first).days < 90,
        }
    except Exception as e:
        return {"present": True, "error": str(e)}


def _schema_contract_probe(spec: "ProducerSpec", path_str: str) -> dict:
    """B748d per CHECKLIST #106(d): schema-contract probe.

    Reads producer source to identify columns the producer requires from its
    cached parquet (df[...] subscripts, f"item_codes" checks, etc.), then
    reads a sample parquet to verify those columns exist.
    """
    path = _REPO / path_str
    if not path.exists():
        return {"present": False}
    try:
        mod = importlib.import_module(spec.module)
        full_src = Path(mod.__file__).read_text(encoding="utf-8")
    except Exception:
        return {"present": True, "error": "cannot read producer source"}
    # B748d: scope to the SPECIFIC producer function (and its helper calls)
    # to avoid catching sibling-producer column references in shared modules
    # (e.g. all 6 congressional_alt_data producers live in one .py).
    func_pat = re.compile(rf'^def {re.escape(spec.func)}\b', re.MULTILINE)
    m = func_pat.search(full_src)
    if not m:
        src = full_src
    else:
        start = m.start()
        next_def = re.search(r"^def \w+", full_src[start + 1:], re.MULTILINE)
        end = start + 1 + next_def.start() if next_def else len(full_src)
        src = full_src[start:end]
    # Only flag column refs the producer body EXPLICITLY guards on.
    required_cols: set[str] = set()
    for m in re.finditer(
        r'["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s+(?:not\s+)?in\s+(?:src|df|sub|window)\.columns',
        src,
    ):
        required_cols.add(m.group(1))
    # Filter out non-column tokens
    required_cols = {c for c in required_cols if not c.startswith("_") and len(c) >= 2}
    # Sample a parquet for actual schema
    try:
        import pandas as pd
        if path.is_file() and path.suffix == ".parquet":
            df = pd.read_parquet(path)
        else:
            files = list(path.rglob("*.parquet"))
            if not files:
                return {"present": True, "no_files": True}
            df = pd.read_parquet(files[0])
        actual_cols = set(df.columns)
        missing = required_cols - actual_cols
        return {
            "present": True,
            "required_cols_detected": sorted(required_cols),
            "actual_cols": sorted(actual_cols),
            "missing_cols": sorted(missing),
            "contract_satisfied": not missing,
        }
    except Exception as e:
        return {"present": True, "error": str(e)}


def _smoke_probe_producer(spec: ProducerSpec, ticker: str, as_of: date) -> tuple[bool, list, str]:
    """Call the producer on a real ticker; return (non_empty, emitted_keys, error).

    For producers with non-standard signatures (compute_pead_signals needs
    ohlcv_df; compute_cross_sectional_features needs ohlcv_dict; etc.) we
    construct minimal synthetic inputs.
    """
    try:
        mod = importlib.import_module(spec.module)
        fn = getattr(mod, spec.func)
        # signature-specific calls
        if spec.func in ("compute_pead_signals", "compute_yoy_surprise_signal"):
            import pandas as pd
            import numpy as np
            # synthetic OHLCV index covering 250 trading days up to as_of
            dates = pd.bdate_range(end=pd.Timestamp(as_of), periods=250)
            ohlcv = pd.DataFrame({
                "open":  np.full(250, 100.0),
                "high":  np.full(250, 101.0),
                "low":   np.full(250, 99.0),
                "close": np.full(250, 100.0),
            }, index=dates)
            result = fn(ticker, ohlcv, as_of)
        elif spec.func == "compute_cross_sectional_features":
            # B746 (2026-06-13): correct signature is (ohlcv_dict, as_of) -- batch producer,
            # not per-ticker. Previous B745 smoke-probe passed ticker as first arg + tripped
            # AttributeError on str.items(); finding (5) re-classified as audit-script bug,
            # not producer bug.
            import pandas as pd
            import numpy as np
            dates = pd.bdate_range(end=pd.Timestamp(as_of), periods=300)
            ohlcv_a = pd.DataFrame({
                "open":  np.linspace(90, 110, 300),
                "high":  np.linspace(91, 111, 300),
                "low":   np.linspace(89, 109, 300),
                "close": np.linspace(90, 110, 300),
                "volume": np.full(300, 1e6),
            }, index=dates)
            ohlcv_b = ohlcv_a * 1.1
            ohlcv_dict = {ticker: ohlcv_a, "MSFT": ohlcv_a, "GOOGL": ohlcv_b, "SPY": ohlcv_a}
            batch_result = fn(ohlcv_dict, as_of)
            # batch returns dict-of-dicts; smoke = our probe ticker's slice
            result = batch_result.get(ticker, {}) if isinstance(batch_result, dict) else {}
        else:
            result = fn(ticker, as_of)
        if not isinstance(result, dict):
            return (False, [], f"non-dict return: {type(result).__name__}")
        return (bool(result), sorted(result.keys()), "")
    except TypeError as e:
        return (False, [], f"signature mismatch: {e}")
    except Exception as e:
        return (False, [], f"exception: {e.__class__.__name__}: {str(e)[:100]}")


def _classify_path(cache_mechanism: str, data_exists: bool, data_row_count: int,
                   smoke_ok: bool, spec: ProducerSpec) -> str:
    """Classify into Path A/B/C/D per the revised B690 sketch.

    Path A: has module-level cache; call as-is
    Path B: no cache; needs one added
    Path C: needs ohlcv_dict / full-universe data (cross_sectional)
    Path D: cache exists but is broken/incomplete OR strategies effectively dead
    """
    if "cross_sectional" in spec.module:
        return "C"
    if cache_mechanism == "none":
        return "B"
    if not data_exists or data_row_count < 10:
        return "D"
    return "A"


def _detect_cache_mechanism(spec: ProducerSpec) -> str:
    """Read the producer source + classify cache mechanism."""
    if not spec.module:
        return "unknown"
    try:
        mod = importlib.import_module(spec.module)
        src_path = Path(mod.__file__)
        src = src_path.read_text(encoding="utf-8")
    except Exception:
        return "unknown"
    if "cross_sectional" in spec.module and "ohlcv_dict" in src:
        return "needs_ohlcv_dict"
    if "@functools.lru_cache" in src or "@lru_cache" in src:
        return "lru_cache"
    if spec.cache_var and f"{spec.cache_var}:" in src or (spec.cache_var and f"{spec.cache_var} =" in src):
        return "module_dict"
    if spec.cache_var and spec.cache_var in src:
        return "module_dict"
    return "none"


def _find_consuming_strategies(signal_keys: tuple) -> list[str]:
    """B748d per CHECKLIST #106(g): grep ALL `backtest/signals/*.py` for
    in-module strategies (not just `screener.py`). The pre-B748d version
    only scanned `screener.py` and missed 4 in-module consumers in
    `backtest/signals/index_rebalance.py` (strategies re-exported into
    screener via aliased imports).
    """
    if not signal_keys:
        return []
    matches: set[str] = set()
    pattern = re.compile(r"^def (strat_\w+)\(s(?:[:\) ]|, )", re.MULTILINE)
    # Scan all signal modules + screener.py
    sig_dir = SCREENER_PATH.parent
    for py_file in sig_dir.glob("*.py"):
        try:
            src = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        # Strip docstrings + comments before searching (don't match references
        # in commentary)
        stripped = re.sub(r'"""[\s\S]*?"""', '', src)
        stripped = re.sub(r"'''[\s\S]*?'''", '', stripped)
        stripped = "\n".join(line.split("#", 1)[0] for line in stripped.splitlines())
        func_spans: list[tuple[str, int, int]] = []
        last_name = None
        last_start = -1
        for m in pattern.finditer(stripped):
            if last_name is not None:
                func_spans.append((last_name, last_start, m.start()))
            last_name = m.group(1)
            last_start = m.start()
        if last_name is not None:
            func_spans.append((last_name, last_start, len(stripped)))
        for name, start, end in func_spans:
            body = stripped[start:end]
            for key in signal_keys:
                if (f'"{key}"' in body or f"'{key}'" in body
                        or f'.get("{key}"' in body or f".get('{key}'" in body):
                    matches.add(name)
                    break
    return sorted(matches)


def _list_all_emitted_keys(spec: ProducerSpec) -> list[str]:
    """Inspect the producer source for ALL constant-string keys assigned to
    its return dict. Used when the curated `consumed_signal_keys` spec is
    incomplete or wrong.
    """
    try:
        mod = importlib.import_module(spec.module)
        src_path = Path(mod.__file__)
        src = src_path.read_text(encoding="utf-8")
    except Exception:
        return []
    # find the function body
    func_pat = re.compile(rf'^def {re.escape(spec.func)}\b', re.MULTILINE)
    m = func_pat.search(src)
    if not m:
        return []
    start = m.start()
    # naive function body: until next top-level def
    next_def = re.search(r"^def \w+", src[start + 1:], re.MULTILINE)
    end = start + 1 + next_def.start() if next_def else len(src)
    body = src[start:end]
    keys: set[str] = set()
    for m2 in re.finditer(r'["\']([a-z_][a-z0-9_]*)["\']\s*:', body):
        keys.add(m2.group(1))
    for m2 in re.finditer(r'out\[\s*["\']([a-z_][a-z0-9_]*)["\']\s*\]', body):
        keys.add(m2.group(1))
    # filter out obvious non-signal keys (likely python kw or internal vars)
    common_noise = {"return", "self", "ticker", "as_of", "df", "out", "result", "value", "default"}
    return sorted(k for k in keys if k not in common_noise)


def audit_all(probe_ticker: str = "AAPL", as_of: date | None = None) -> list[ProducerAuditRow]:
    if as_of is None:
        as_of = date(2024, 6, 28)
    rows: list[ProducerAuditRow] = []
    for spec in PRODUCERS:
        mechanism = _detect_cache_mechanism(spec)
        data_exists, n_rows, n_tickers = _probe_data_path(spec.data_path)
        smoke_ok, smoke_keys, smoke_err = _smoke_probe_producer(spec, probe_ticker, as_of)
        path = _classify_path(mechanism, data_exists, n_rows, smoke_ok, spec)
        # Widened key set: union of curated + AST-detected emitted keys
        ast_keys = _list_all_emitted_keys(spec)
        all_keys = tuple(sorted(set(spec.consumed_signal_keys) | set(ast_keys)))
        consumers = _find_consuming_strategies(all_keys)

        # B748d per CHECKLIST #106 -- new probes
        producer_source_path = _discover_producer_path(spec)
        # Use producer-source-discovered path for the more rigorous probes;
        # fall back to registry hardcoded path
        probe_path = producer_source_path or spec.data_path
        temporal = _temporal_coverage_probe(probe_path)
        schema = _schema_contract_probe(spec, probe_path)
        # Synthesize issue flags per #106(c)+(d)
        flags: list[str] = []
        if temporal.get("present") and temporal.get("is_stale"):
            flags.append(f"STALE_last={temporal.get('last_date')}_{temporal.get('gap_days_at_end')}d_to_window_end")
        if temporal.get("present") and temporal.get("is_narrow_window"):
            flags.append(f"NARROW_window={temporal.get('first_date')}_to_{temporal.get('last_date')}")
        if temporal.get("present") and temporal.get("covers_window_start") is False:
            flags.append(f"LATE_START_first={temporal.get('first_date')}")
        if schema.get("present") and schema.get("missing_cols"):
            flags.append(f"SCHEMA_MISSING_COLS={schema.get('missing_cols')}")
        # B748d: normalize Windows backslash to forward slash for comparison
        norm = lambda s: s.replace("\\", "/") if s else s
        if producer_source_path and norm(producer_source_path) != norm(spec.data_path):
            flags.append(
                f"REGISTRY_PATH_DRIFT_registry={spec.data_path}_actual={producer_source_path}"
            )

        rows.append(ProducerAuditRow(
            producer=spec.func,
            module=spec.module.split(".")[-1],
            cache_var=spec.cache_var,
            cache_mechanism=mechanism,
            path_classification=path,
            data_path=spec.data_path,
            data_exists=data_exists,
            data_row_count=n_rows,
            data_unique_tickers=n_tickers,
            smoke_emits_non_empty=smoke_ok,
            smoke_signal_keys=smoke_keys[:8],
            smoke_error=smoke_err,
            consumed_signal_keys=list(all_keys),
            consuming_strategies=consumers,
            producer_source_path=producer_source_path,
            temporal_coverage=temporal,
            schema_contract=schema,
            issue_flags=flags,
        ))
    return rows


def render_report(rows: list[ProducerAuditRow], probe_ticker: str, as_of: date) -> str:
    L = [
        "# B745 TIER 2 Producer Audit Report (finding-grade)",
        "",
        f"# Source: scripts/audit_tier2_producer_caches.py per CHECKLIST #77",
        "",
        f"Probe ticker: `{probe_ticker}`  |  Probe as_of: `{as_of}`  |  Total producers audited: **{len(rows)}**",
        "",
        "## Headline finding (pre-audit investigation, 2026-06-13)",
        "",
        "**The B689 audit claim that `patentmomentum` and `corporatedonors` had STUB caches (1 entry each) is FALSE.**",
        "Direct probe of the underlying parquets:",
        "- `data_prefetch/quiver/patentmomentum/global.parquet`: **5,830,800 rows** (5.8M; 6.9MB)",
        "- `data_prefetch/quiver/corporatedonors/global.parquet`: **25,000 rows** across 432 unique tickers",
        "",
        "This means the 'silent-gap risk' framing inverts: data IS present.",
        "The audit below confirms whether each producer READS + EMITS correctly + whether consuming strategies actually fire.",
        "",
        "## Per-producer classification",
        "",
        "| # | Producer | Module | Mechanism | Path | Data rows | Unique tickers | Smoke emits | Smoke keys | Error |",
        "|---|---|---|---|---|---:|---:|---|---|---|",
    ]
    for i, r in enumerate(rows, 1):
        L.append(f"| {i} | `{r.producer}` | `{r.module}` | {r.cache_mechanism} | **{r.path_classification}** | "
                 f"{r.data_row_count:,} | {r.data_unique_tickers:,} | {'YES' if r.smoke_emits_non_empty else 'NO'} | "
                 f"{', '.join(r.smoke_signal_keys[:3]) or '(empty)'} | {r.smoke_error[:60] or ''} |")
    L.extend([
        "",
        "## Path classification summary",
        "",
    ])
    by_path: dict[str, list[ProducerAuditRow]] = {"A": [], "B": [], "C": [], "D": []}
    for r in rows:
        by_path[r.path_classification].append(r)
    for path, label in [
        ("A", "PATH A -- existing module-level cache; call as-is in measure_fire_count.py"),
        ("B", "PATH B -- no cache; needs module-level cache added"),
        ("C", "PATH C -- needs ohlcv_dict or full-universe data"),
        ("D", "PATH D -- data missing/sparse/broken; consuming strategies may be effectively dead"),
    ]:
        items = by_path[path]
        L.append(f"### {label}  ({len(items)} producers)")
        L.append("")
        if not items:
            L.append("_(none)_")
            L.append("")
            continue
        for r in items:
            L.append(f"- **`{r.producer}`** ({r.module})")
            L.append(f"    - data: `{r.data_path}` -- rows={r.data_row_count:,}, tickers={r.data_unique_tickers:,}")
            L.append(f"    - smoke: emits={r.smoke_emits_non_empty}, error={r.smoke_error or 'none'}")
            if r.consuming_strategies:
                L.append(f"    - consumed by {len(r.consuming_strategies)} strategy(s): {', '.join(r.consuming_strategies[:6])}{'...' if len(r.consuming_strategies) > 6 else ''}")
        L.append("")

    # Path D dead-strategy finding section
    if by_path["D"]:
        L.append("## DEAD-STRATEGY FINDING")
        L.append("")
        L.append("Path D producers' consuming strategies have been firing on the OTHER gates only -- the distinguishing signal has been `{}`. This is the same orphan-emitter class as SM-5 + SMC vendored-library SPOF. Each is a Pattern F input (delete-vs-revive decision), not engineering housekeeping.")
        L.append("")
        for r in by_path["D"]:
            L.append(f"### `{r.producer}` -- {len(r.consuming_strategies)} possibly-dead strategy(s)")
            L.append("")
            for strat in r.consuming_strategies:
                L.append(f"  - `{strat}` -- consumes {r.consumed_signal_keys}; distinguishing signal absent")
            L.append("")

    L.append("---")
    L.append("")
    L.append("## Owner action items")
    L.append("")
    L.append("- **Path A producers**: wire directly in B752 (measure_fire_count.py `_compute_tier2_signals_for_bar` helper); no producer-side changes.")
    L.append("- **Path B producers** (if any): add module-level `_BY_TICKER` cache in B749/B750 per-producer mini-batches.")
    L.append("- **Path C producer** (cross_sectional): B751 ships `_compute_cross_sectional_signals_for_date` harness helper -- ONLY AFTER B746 PIT-invariance audit PASSES.")
    L.append("- **Path D producers** (if any): B748 ships loud-failure wrappers + queues dead-strategy Pattern F tickets per consuming strategy.")
    return "\n".join(L)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--probe-ticker", default="AAPL")
    p.add_argument("--as-of", default="2024-06-28")
    p.add_argument("--json", default=str(OUT_DIR / "b745_audit_results.json"))
    p.add_argument("--md", default=str(OUT_DIR / "b745_audit_report.md"))
    args = p.parse_args()
    as_of = date.fromisoformat(args.as_of)

    print(f"[B745] Auditing {len(PRODUCERS)} TIER 2 producers on probe ticker={args.probe_ticker} as_of={as_of}")
    rows = audit_all(probe_ticker=args.probe_ticker, as_of=as_of)

    print(f"[B745] Classification summary:")
    by_path: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0}
    for r in rows:
        by_path[r.path_classification] += 1
    for path in ("A", "B", "C", "D"):
        print(f"         Path {path}: {by_path[path]} producer(s)")

    md_text = render_report(rows, args.probe_ticker, as_of)
    Path(args.md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.md).write_text(md_text, encoding="utf-8")
    Path(args.json).write_text(
        json.dumps({"probe_ticker": args.probe_ticker, "as_of": str(as_of),
                    "rows": [asdict(r) for r in rows]}, indent=2),
        encoding="utf-8",
    )
    print(f"[B745] WROTE {args.md}")
    print(f"[B745] WROTE {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
