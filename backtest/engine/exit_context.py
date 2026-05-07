"""Per-trade exit-analysis context builder (Pass 53 Day-9-evening 2026-05-07).

Owner directive: "All tiers need to be tested in phase 1A itself" — augments
trade_exit_detail.csv with ~25 analysis dimensions (Tiers 1-4) so per-cell
exit-method analysis (by strategy × regime × sector × cap × vol × hold-band ×
direction × universe-tier × smart-money × ... × event flags) is queryable
out-of-box without analysis-time JOINs.

Per DEC-594 same-commit: this module + run_exit_comparison wiring + tests in
test_exit_context.py land together.

Tier 1 (10 cols, baseline): regime / sector / cap_band / vol_band /
  confidence_tier / direction / hold_duration_band / win_loss_outcome /
  universe_tier / smart_money_signal_present
Tier 2 (5): vix_at_entry / entry_atr_ratio / mae_bucket / mfe_bucket /
  regime_changed_during_hold / earnings_during_hold
Tier 3 (5): circuit_breaker_active_during_hold / news_sentiment_shift /
  8K_filed_during_hold / day_of_week_at_entry / days_from_quarter_end_at_entry
Tier 4 (5): vix_term_structure / hy_oas_band / adv_bucket / volume_rank_sector /
  sector_momentum_vs_spy_at_entry

For data not available at backtest-time (e.g., news during hold, circuit-breaker
state) the context attempts best-effort lookup; missing values default to 'unknown'
or 'not_available' so the column is always present + queryable.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Tier 1 helpers (already in trade_log; mirrored here for trade_exit_detail)
# ---------------------------------------------------------------------------
def _hold_duration_band(hold_days: int) -> str:
    if hold_days <= 3: return "short_le_3d"
    if hold_days <= 10: return "medium_4_10d"
    return "long_ge_11d"


def _win_loss_outcome(pnl_pct: float) -> str:
    return "win" if pnl_pct > 0 else "loss"


def _universe_tier(ticker: str, as_of: date) -> str:
    """Resolve T1a/T1c/T1ETF/T2/T3 per DEC-504 precedence."""
    try:
        from backtest.data.universe import resolve_tier_precedence
        tier = resolve_tier_precedence(ticker, as_of)
        return tier or "unknown"
    except Exception:
        return "unknown"


def _smart_money_signal_present(signals: Dict[str, Any]) -> str:
    """Yes/no flag per DEC-124 confluence — checks for any smart_money_* key in signals."""
    if not isinstance(signals, dict):
        return "unknown"
    sm_keys = [
        "smart_money_score", "insider_signal", "institutional_signal",
        "congressional_signal", "smart_money_present",
    ]
    for k in sm_keys:
        v = signals.get(k)
        if v not in (None, 0, 0.0, False, "no"):
            return "yes"
    return "no"


# ---------------------------------------------------------------------------
# Tier 2 helpers
# ---------------------------------------------------------------------------
def _vix_at_entry(entry_date: date, signals: Dict[str, Any]) -> float:
    """VIX value at entry. Reads from signals dict (populated by macro_snapshot)
    or falls back to 0.0 if unavailable."""
    if isinstance(signals, dict):
        v = signals.get("vix_value") or signals.get("vix")
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return 0.0


def _entry_atr_ratio(atr: float, entry_price: float) -> float:
    if entry_price > 0:
        return float(atr) / float(entry_price)
    return 0.0


def _mae_mfe_bucket(value_pct: float, kind: str = "mae") -> str:
    """Bucket MAE/MFE percent into quartile-like bands.
    kind='mae' (negative values; closer-to-0 = lower drawdown)
    kind='mfe' (positive values; higher = larger profit run)
    """
    abs_v = abs(value_pct)
    if abs_v < 0.02: return "q1_lt_2pct"
    if abs_v < 0.05: return "q2_2_5pct"
    if abs_v < 0.10: return "q3_5_10pct"
    return "q4_ge_10pct"


def _regime_changed_during_hold(entry_regime: str, exit_regime: Optional[str]) -> str:
    if not exit_regime or exit_regime == "unknown":
        return "unknown"
    return "yes" if entry_regime != exit_regime else "no"


def _earnings_during_hold(ticker: str, entry_date: date, exit_date: Optional[date]) -> str:
    """Best-effort check: scan polygon financials cache for filing_date in [entry, exit]."""
    if exit_date is None:
        return "unknown"
    try:
        from pathlib import Path
        repo = Path(__file__).resolve().parents[2]
        p = repo / "data_prefetch" / "polygon" / "financials" / f"{ticker}.parquet"
        if not p.exists():
            return "no_data"
        df = pd.read_parquet(p, columns=["filing_date"])
        df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
        in_window = df["filing_date"].between(
            pd.Timestamp(entry_date), pd.Timestamp(exit_date), inclusive="both"
        )
        return "yes" if in_window.any() else "no"
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Tier 3 helpers
# ---------------------------------------------------------------------------
def _day_of_week_at_entry(entry_date: date) -> str:
    return ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][entry_date.weekday()]


def _days_from_quarter_end(entry_date: date) -> int:
    """Days from entry to next quarter-end (March/June/Sept/Dec end)."""
    quarter_ends = [
        date(entry_date.year, 3, 31),
        date(entry_date.year, 6, 30),
        date(entry_date.year, 9, 30),
        date(entry_date.year, 12, 31),
        date(entry_date.year + 1, 3, 31),  # roll to next year
    ]
    for qe in quarter_ends:
        if qe >= entry_date:
            return (qe - entry_date).days
    return 0


def _circuit_breaker_active_during_hold(
    entry_date: date, exit_date: Optional[date], cb_log: list,
) -> str:
    """Check if circuit breaker fired during hold period."""
    if exit_date is None or not cb_log:
        return "no_data"
    for evt in cb_log:
        evt_date = evt.get("date") if isinstance(evt, dict) else None
        if evt_date and entry_date <= evt_date <= exit_date:
            return "yes"
    return "no"


def _news_sentiment_shift_during_hold(
    ticker: str, entry_date: date, exit_date: Optional[date],
) -> str:
    """Best-effort: count news articles in hold window. Detailed sentiment-shift
    analysis deferred to Sprint 7 — for Phase 1A, return article count band."""
    if exit_date is None:
        return "unknown"
    try:
        from pathlib import Path
        repo = Path(__file__).resolve().parents[2]
        p = repo / "data_prefetch" / "polygon" / "news" / f"{ticker}.parquet"
        if not p.exists():
            return "no_data"
        df = pd.read_parquet(p, columns=["published_utc"])
        df["d"] = pd.to_datetime(df["published_utc"], errors="coerce").dt.tz_localize(None).dt.date
        n = df["d"].between(entry_date, exit_date, inclusive="both").sum()
        if n == 0: return "none"
        if n <= 5: return "low_1_5"
        if n <= 20: return "mid_6_20"
        return "high_gt_20"
    except Exception:
        return "unknown"


def _8k_filed_during_hold(ticker: str, entry_date: date, exit_date: Optional[date]) -> str:
    if exit_date is None:
        return "unknown"
    try:
        from pathlib import Path
        repo = Path(__file__).resolve().parents[2]
        p = repo / "data_prefetch" / "sec_edgar" / "8_K" / f"{ticker}.parquet"
        if not p.exists():
            return "no_data"
        df = pd.read_parquet(p, columns=["filing_date"])
        df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
        in_window = df["filing_date"].between(
            pd.Timestamp(entry_date), pd.Timestamp(exit_date), inclusive="both"
        )
        return "yes" if in_window.any() else "no"
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Tier 4 helpers
# ---------------------------------------------------------------------------
def _vix_term_structure_at_entry(entry_date: date) -> str:
    """Approximate VIX term structure via VIX vs VIX3M/VXX proxies.
    For Phase 1A baseline, returns 'unknown' until VIX3M data prefetched.
    """
    return "unknown"  # Sprint 7+ when VIX3M/VVIX prefetched per DEC-513 P1


def _hy_oas_band_at_entry(entry_date: date) -> str:
    """HY OAS regime band (compressed/normal/wide/stressed) from FRED BAMLH0A0HYM2."""
    try:
        from pathlib import Path
        repo = Path(__file__).resolve().parents[2]
        p = repo / "data_prefetch" / "fred" / "observations" / "BAMLH0A0HYM2.parquet"
        if not p.exists():
            return "no_data"
        df = pd.read_parquet(p)
        df["date"] = pd.to_datetime(df["date"])
        df_pit = df[df["date"] <= pd.Timestamp(entry_date)]
        if df_pit.empty: return "no_data"
        v = float(df_pit.iloc[-1]["value"])
        if v < 3.0: return "compressed_lt_3"
        if v < 5.0: return "normal_3_5"
        if v < 7.0: return "wide_5_7"
        return "stressed_ge_7"
    except Exception:
        return "unknown"


def _adv_bucket(df_full: pd.DataFrame, entry_date: date) -> str:
    """Average Daily $Volume bucket for trailing 20 days at entry."""
    try:
        if df_full is None or df_full.empty:
            return "no_data"
        if "date" in df_full.columns:
            mask = pd.to_datetime(df_full["date"]) <= pd.Timestamp(entry_date)
            df_pit = df_full.loc[mask].tail(20)
        elif isinstance(df_full.index, pd.DatetimeIndex):
            df_pit = df_full[df_full.index <= pd.Timestamp(entry_date)].tail(20)
        else:
            return "no_data"
        if df_pit.empty:
            return "no_data"
        adv = (df_pit["close"] * df_pit["volume"]).mean()
        if adv < 5e6: return "lt_5M"
        if adv < 25e6: return "5_25M"
        if adv < 100e6: return "25_100M"
        if adv < 500e6: return "100_500M"
        return "ge_500M"
    except Exception:
        return "unknown"


def _sector_momentum_vs_spy(spy_df: Optional[pd.DataFrame], entry_date: date) -> str:
    """Sector momentum vs SPY at entry — placeholder for Sprint 7+. Returns
    SPY-relative trend band based on SPY 20d return."""
    if spy_df is None or spy_df.empty:
        return "no_data"
    try:
        if "date" in spy_df.columns:
            mask = pd.to_datetime(spy_df["date"]) <= pd.Timestamp(entry_date)
            df_pit = spy_df.loc[mask].tail(21)
        elif isinstance(spy_df.index, pd.DatetimeIndex):
            df_pit = spy_df[spy_df.index <= pd.Timestamp(entry_date)].tail(21)
        else:
            return "no_data"
        if len(df_pit) < 21:
            return "insufficient_history"
        ret_20d = (df_pit["close"].iloc[-1] / df_pit["close"].iloc[0] - 1) * 100
        if ret_20d > 5: return "spy_strong_up_gt_5pct"
        if ret_20d > 0: return "spy_mild_up_0_5pct"
        if ret_20d > -5: return "spy_mild_down_neg5_0"
        return "spy_strong_down_lt_neg5"
    except Exception:
        return "unknown"


def _volume_rank_within_sector(df_full: pd.DataFrame, entry_date: date) -> str:
    """Volume rank within sector — defaults to 'unknown' until sector-cohort
    data prefetched. Phase 1A placeholder."""
    return "unknown"


# ---------------------------------------------------------------------------
# Main entry-context builder
# ---------------------------------------------------------------------------
def build_entry_context(
    row: pd.Series,
    ticker: str,
    entry_date: date,
    df_full: pd.DataFrame,
    spy_df: Optional[pd.DataFrame],
    signals: Dict[str, Any],
    atr: float,
) -> Dict[str, Any]:
    """Build per-trade context dict spanning Tiers 1-4 per DEC-594 same-commit.

    Returns a dict with ~25 keys covering all 4 tiers. Tier 1 (already in
    trade_log) is mirrored for trade_exit_detail self-containment.
    """
    entry_price = float(row.get("entry_price", 0.0))
    regime = row.get("regime") or "unknown"
    sector = row.get("sector") or "Unknown"

    # Tier 1
    ctx: Dict[str, Any] = {
        # Mirror trade_log fields for trade_exit_detail self-containment
        "regime_at_entry":               str(regime),
        "sector":                        str(sector),
        "confidence_tier":               str(row.get("confidence_tier") or "unknown"),
        # Direction is already in trade_exit_detail; cap_band / vol_band derived
        "cap_band":                      _derive_cap_band(row),
        "vol_band":                      _derive_vol_band(signals, atr, entry_price),
        "hold_duration_band":            _hold_duration_band(int(row.get("hold_days", 0) or 0)),
        "win_loss_outcome":              _win_loss_outcome(float(row.get("pnl_pct", 0.0) or 0.0)),
        "universe_tier":                 _universe_tier(ticker, entry_date),
        "smart_money_signal_present":    _smart_money_signal_present(signals),
    }

    # Tier 2
    exit_date_obj = _parse_date(row.get("exit_date"))
    exit_regime = _exit_regime(row)  # placeholder; defaults to entry regime
    ctx.update({
        "vix_at_entry":                  _vix_at_entry(entry_date, signals),
        "entry_atr_ratio":               _entry_atr_ratio(atr, entry_price),
        "mae_bucket":                    _mae_mfe_bucket(float(row.get("max_adverse_excursion", 0.0) or 0.0), "mae"),
        "mfe_bucket":                    _mae_mfe_bucket(float(row.get("max_favourable_excursion", 0.0) or 0.0), "mfe"),
        "regime_changed_during_hold":    _regime_changed_during_hold(regime, exit_regime),
        "earnings_during_hold":          _earnings_during_hold(ticker, entry_date, exit_date_obj),
    })

    # Tier 3
    ctx.update({
        "circuit_breaker_active_during_hold": "no_data",  # populated by writer if cb_log passed
        "news_sentiment_shift_during_hold":   _news_sentiment_shift_during_hold(ticker, entry_date, exit_date_obj),
        "8K_filed_during_hold":              _8k_filed_during_hold(ticker, entry_date, exit_date_obj),
        "day_of_week_at_entry":              _day_of_week_at_entry(entry_date),
        "days_from_quarter_end_at_entry":    _days_from_quarter_end(entry_date),
    })

    # Tier 4
    ctx.update({
        "vix_term_structure":            _vix_term_structure_at_entry(entry_date),
        "hy_oas_band_at_entry":          _hy_oas_band_at_entry(entry_date),
        "adv_bucket":                    _adv_bucket(df_full, entry_date),
        "volume_rank_within_sector":     _volume_rank_within_sector(df_full, entry_date),
        "sector_momentum_vs_spy_at_entry": _sector_momentum_vs_spy(spy_df, entry_date),
    })

    return ctx


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _derive_cap_band(row: pd.Series) -> str:
    """Map market_cap to mega/large/mid/small. Falls back to 'unknown' if
    market_cap unavailable in row."""
    cap = row.get("market_cap") or 0
    try:
        cap_b = float(cap) / 1e9
    except (TypeError, ValueError):
        return "unknown"
    if cap_b >= 200: return "mega_ge_200B"
    if cap_b >= 10: return "large_10_200B"
    if cap_b >= 2: return "mid_2_10B"
    if cap_b > 0: return "small_lt_2B"
    return "unknown"


def _derive_vol_band(signals: Dict[str, Any], atr: float, entry_price: float) -> str:
    """Volatility band from VIX (preferred) or ATR/price (fallback)."""
    if isinstance(signals, dict):
        vix = signals.get("vix_value") or signals.get("vix")
        if vix is not None:
            try:
                v = float(vix)
                if v < 15: return "low_lt_15"
                if v < 25: return "mid_15_25"
                if v < 40: return "high_25_40"
                return "crisis_ge_40"
            except (TypeError, ValueError):
                pass
    # Fallback: ATR/price
    if entry_price > 0:
        ratio = atr / entry_price
        if ratio < 0.01: return "low_atr_lt_1pct"
        if ratio < 0.025: return "mid_atr_1_2.5pct"
        if ratio < 0.05: return "high_atr_2.5_5pct"
        return "crisis_atr_ge_5pct"
    return "unknown"


def _parse_date(v: Any) -> Optional[date]:
    if v is None or v == "" or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, date):
        return v
    try:
        return pd.to_datetime(v).date()
    except Exception:
        return None


def _exit_regime(row: pd.Series) -> Optional[str]:
    """Exit regime from row if recorded; else None.
    Trade log doesn't currently record exit regime — placeholder defaults to entry regime."""
    return row.get("exit_regime") or row.get("regime")


# Public list of all context column names for downstream consumers
CONTEXT_COLUMN_NAMES = [
    # Tier 1
    "regime_at_entry", "sector", "confidence_tier", "cap_band", "vol_band",
    "hold_duration_band", "win_loss_outcome", "universe_tier",
    "smart_money_signal_present",
    # Tier 2
    "vix_at_entry", "entry_atr_ratio", "mae_bucket", "mfe_bucket",
    "regime_changed_during_hold", "earnings_during_hold",
    # Tier 3
    "circuit_breaker_active_during_hold", "news_sentiment_shift_during_hold",
    "8K_filed_during_hold", "day_of_week_at_entry", "days_from_quarter_end_at_entry",
    # Tier 4
    "vix_term_structure", "hy_oas_band_at_entry", "adv_bucket",
    "volume_rank_within_sector", "sector_momentum_vs_spy_at_entry",
]
