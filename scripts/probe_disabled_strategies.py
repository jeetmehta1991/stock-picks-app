"""scripts/probe_disabled_strategies.py (B1475, ticket S6-B1473a) -- RUNTIME proof that the
disable sets actually exclude their members on the engine's real call path.

WHY THIS EXISTS
B1465 disabled three duplicate strategies and I verified it by reading `config.py` and counting
the registry. That is exactly what `feedback_wired_means_engine_consumed` forbids -- "wired" means
engine-consumed on a real call path, not present in a set. A skip branch can be added to a function
nobody reaches, guarded by a condition that never holds, or shadowed by an earlier `continue`, and
every one of those failures reads identically to success in the source.

WHAT THIS DOES
Calls `screen_instrument()` -- the function that owns the skip loop (screener.py:8520) -- on
synthetic but permissive inputs, and asserts that no disabled strategy appears among the returned
candidates while at least one ENABLED strategy does. The second half matters: if the probe fires
nothing at all, "no disabled strategy fired" is vacuously true and proves nothing, which is the
L314/L322 failure class (a probe that never ran reading as a pass).
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.config import (  # noqa: E402
    DEPRECATED_STRATEGIES, STRATEGIES_DISABLED_DATA_SCARCITY,
    STRATEGIES_DISABLED_DUPLICATE, STRATEGIES_DISABLED_MISSING_PRODUCER,
)
from backtest.signals.screener import ALL_STRATEGIES, screen_instrument  # noqa: E402

BLOCKED = (set(DEPRECATED_STRATEGIES) | set(STRATEGIES_DISABLED_DATA_SCARCITY)
           | set(STRATEGIES_DISABLED_DUPLICATE) | set(STRATEGIES_DISABLED_MISSING_PRODUCER))


def _synthetic_ohlcv(n: int = 400) -> pd.DataFrame:
    """A trending series with volume, enough history for long-lookback producers."""
    rng = np.random.default_rng(11)
    idx = pd.bdate_range(end=pd.Timestamp("2025-06-02"), periods=n)
    close = 100 * np.cumprod(1 + rng.normal(0.0012, 0.012, n))
    high = close * (1 + abs(rng.normal(0.004, 0.003, n)))
    low = close * (1 - abs(rng.normal(0.004, 0.003, n)))
    return pd.DataFrame({"open": close * 0.999, "high": high, "low": low, "close": close,
                         "volume": rng.integers(2_000_000, 9_000_000, n)}, index=idx)


def main() -> int:
    print("=" * 96)
    print("RUNTIME DISABLE PROBE (B1475 / S6-B1473a) -- engine call path, not source inspection")
    print("=" * 96)
    print(f"  registered {len(ALL_STRATEGIES)} | blocked {len(BLOCKED)} "
          f"(duplicate {len(STRATEGIES_DISABLED_DUPLICATE)}, "
          f"scarcity {len(STRATEGIES_DISABLED_DATA_SCARCITY)})")

    # B1475: synthetic OHLCV fires nothing - most producers need real cached history and the
    # probe correctly HALTed rather than reporting a vacuous pass. Use a real cached ticker.
    cache = REPO / "backtest" / "data" / "cache" / "ohlcv"
    real = None
    for cand in ("AAPL.parquet", "MSFT.parquet", "SPY.parquet"):
        if (cache / cand).exists():
            real = cache / cand
            break
    if real is not None:
        d = pd.read_parquet(real)
        dcol = "date" if "date" in d.columns else d.columns[0]
        d[dcol] = pd.to_datetime(d[dcol])
        d = d.set_index(dcol).sort_index()
        d.columns = [c.lower() for c in d.columns]
        df = d[d.index <= pd.Timestamp("2025-06-02")].tail(500)
        print(f"  using REAL cached history: {real.name}, {len(df)} bars "
              f"{df.index.min().date()}..{df.index.max().date()}")
    else:
        df = _synthetic_ohlcv()
        print("  [WARN] no cached ticker found; falling back to synthetic (likely to fire nothing)")
    fired: set[str] = set()
    for regime in ("bull", "neutral", "bear"):
        try:
            out = screen_instrument(
                ticker="PROBE", df=df, info={"sector": "Technology", "marketCap": 5e10},
                as_of=date(2025, 6, 2), regime=regime, vix_value=18.0,
                vix_history=pd.Series([18.0] * 60), xs_features={},
            )
        except Exception as e:  # preflight-allow: probe-report
            print(f"  [WARN] regime={regime} raised {type(e).__name__}: {str(e)[:90]}")
            continue
        for c in (out or []):
            nm = (c.get("strategy") if isinstance(c, dict) else getattr(c, "strategy", None))
            if nm:
                fired.add(str(nm).replace("strat_", ""))

    print(f"\n  distinct strategies that fired across 3 regimes: {len(fired)}")

    # HALF 1 -- the probe must actually exercise the path, or the next assertion is vacuous
    if not fired:
        print("  [HALT] nothing fired. 'No disabled strategy fired' would be vacuously true, "
              "which proves nothing (the L314/L322 class). Probe inputs need loosening.")
        return 1
    print("  [OK] the path is exercised - at least one enabled strategy fired")

    # HALF 2 -- no blocked strategy may appear
    leaked = sorted(fired & BLOCKED)
    if leaked:
        print(f"  [FAIL] DISABLED strategies reached the candidate list: {leaked}")
        return 1
    print(f"  [OK] zero of the {len(BLOCKED)} blocked strategies reached the candidate list")

    dup_hit = sorted(fired & set(STRATEGIES_DISABLED_DUPLICATE))
    print(f"  [OK] B1465 duplicates specifically: {len(dup_hit)} leaked "
          f"(of {len(STRATEGIES_DISABLED_DUPLICATE)} disabled)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
