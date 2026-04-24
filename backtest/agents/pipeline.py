"""
agents/pipeline.py — TradingAgents multi-agent analysis pipeline.

Six agents analyse each candidate instrument:
  1. Technical Agent     — confirms all indicator signals at exact historical date
  2. Fundamental Agent   — earnings risk, buybacks, analyst revisions, insider/13F
  3. Sentiment Agent     — news, congressional trades, AAII, Fear/Greed, social
  4. Risk Agent          — yield curve, VIX, DXY, short interest, economic calendar
  5. Bull/Bear Agents    — debate the full signal set
  6. Decision Agent      — final combined confidence score

Model selection per project plan section 4.10:
  Phase 1A/1B: claude-haiku  (~$0.021/analysis)
  Phase 1C/1D: claude-sonnet (~$0.080/analysis)

All agents are called via the Anthropic API. ANTHROPIC_API_KEY env var required.
"""

import json
import logging
import os
import time
from datetime import date
from typing import Optional

import requests

from backtest.config import AI_MODELS, ANTHROPIC_API_URL

logger = logging.getLogger(__name__)

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Rate-limit safety: Haiku allows ~50 req/min on free tier; keep under that.
_API_DELAY_SEC = 1.5


def _call_claude(
    prompt: str,
    model: str,
    system: str = "",
    max_tokens: int = 800,
) -> Optional[str]:
    """
    Call Anthropic API and return the text response.
    Returns None on failure.
    """
    if not ANTHROPIC_KEY:
        logger.error("ANTHROPIC_API_KEY not set — agents unavailable")
        return None

    headers = {
        "x-api-key":         ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json",
    }
    payload = {
        "model":      model,
        "max_tokens": max_tokens,
        "messages":   [{"role": "user", "content": prompt}],
    }
    if system:
        payload["system"] = system

    for attempt in range(3):
        try:
            resp = requests.post(
                ANTHROPIC_API_URL,
                headers=headers,
                json=payload,
                timeout=60,
            )
            if resp.status_code == 529 or resp.status_code == 429:
                wait = 30 * (attempt + 1)
                logger.warning("API rate limit (attempt %d) — sleeping %ds", attempt + 1, wait)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]
        except Exception as exc:
            logger.error("Claude API call failed (attempt %d): %s", attempt + 1, exc)
            if attempt < 2:
                time.sleep(5)

    return None


def _parse_json_response(text: Optional[str]) -> dict:
    """Parse JSON from agent response, with cleanup for markdown fences."""
    if not text:
        return {}
    clean = text.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")
        clean = "\n".join(lines[1:-1]) if len(lines) > 2 else clean
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Try to extract JSON from mixed text
        import re
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {}


SYSTEM_ANALYST = """You are a quantitative trading analyst. You analyse stock trading signals
objectively and output structured JSON only. Never include preamble or explanation outside the JSON.
Be concise and precise. Base your analysis strictly on the data provided — no hallucination."""


# ---------------------------------------------------------------------------
# AGENT 1: TECHNICAL AGENT
# ---------------------------------------------------------------------------

def run_technical_agent(
    ticker: str,
    as_of: date,
    signals: dict,
    strategies_triggered: list,
    model: str,
) -> dict:
    """
    Technical Agent: confirms all indicator signals at exact historical date.
    Returns: tech_score (0-10), confirmations, warnings, summary
    """
    # Select most relevant signals to keep prompt concise (cost control)
    key_signals = {
        k: v for k, v in signals.items()
        if isinstance(v, bool) or k in [
            "rsi_14", "rsi_9", "adx", "macd_12_26_9_hist",
            "stoch_k", "vix", "vol_ratio_20d", "cmf",
            "bb_20_20_bandwidth", "atr",
        ]
    }

    # Sector halo effect context
    sector = signals.get("sector", "Unknown")
    sector_etf = signals.get("sector_etf", "SPY")
    sector_etf_return = signals.get("sector_etf_return_pct", 0.0)
    sector_context = f"{sector_etf} (sector ETF) returned {sector_etf_return:+.2f}% today"
    halo = "tailwind" if sector_etf_return > 1.0 else "headwind" if sector_etf_return < -1.0 else "neutral"

    prompt = f"""Analyse technical signals for {ticker} ({sector}) as of {as_of}.

Strategies triggered: {strategies_triggered}

Sector context: {sector_context} — sector momentum is {halo} for this trade.

Key signals:
{json.dumps(key_signals, indent=2, default=str)}

Evaluate: signal quality, confluence strength, sector momentum alignment, and whether this is a high-probability swing entry.

Return JSON only:
{{
  "tech_score": <integer 0-10>,
  "strongest_signals": [<list of top 3 signal names>],
  "concerns": [<list of any conflicting or weak signals>],
  "sector_alignment": "<tailwind|neutral|headwind>",
  "entry_quality": "<strong|moderate|weak>",
  "summary": "<one sentence>"
}}"""

    resp = _call_claude(prompt, model, SYSTEM_ANALYST)
    time.sleep(_API_DELAY_SEC)
    result = _parse_json_response(resp)
    return result if result else {
        "tech_score": 5, "entry_quality": "moderate",
        "summary": "Technical Agent unavailable",
    }


# ---------------------------------------------------------------------------
# AGENT 2: FUNDAMENTAL AGENT
# ---------------------------------------------------------------------------

def _load_social_data(ticker: str, as_of: date) -> dict:
    """Load pre-fetched WallStreetBets + Wikipedia data."""
    quiver_dir = Path(__file__).parent.parent / "data" / "cache" / "quiver"
    result = {"wsb_mentions": 0, "wsb_trend": "none", "wiki_views": 0}

    for data_type, key in [("wallstreetbets", "wsb"), ("wikipedia", "wiki")]:
        path = quiver_dir / data_type / f"{ticker.replace('-','_')}.parquet"
        if not path.exists():
            continue
        try:
            df = pd.read_parquet(path)
            if df.empty:
                continue
            df["Date"] = pd.to_datetime(df["Date"])
            window = df[df["Date"] <= pd.Timestamp(as_of)].tail(30)
            if key == "wsb" and "Mentions" in df.columns:
                result["wsb_mentions"] = int(window["Mentions"].sum())
                recent = window.tail(7)["Mentions"].mean()
                older = window.head(23)["Mentions"].mean() if len(window) > 7 else recent
                result["wsb_trend"] = "rising" if recent > older * 1.2 else "falling" if recent < older * 0.8 else "stable"
            elif key == "wiki" and "Views" in df.columns:
                result["wiki_views"] = int(window["Views"].mean())
        except Exception:
            pass
    return result


def run_fundamental_agent(
    ticker: str,
    as_of: date,
    insider_sig: dict,
    institutional_sig: dict,
    earnings_days: Optional[int],
    model: str,
) -> dict:
    """
    Fundamental Agent: earnings risk, insider/13F, WallStreetBets, Wikipedia.
    Returns: fundamental_score (0-10), earnings_risk, smart_money_alignment, summary
    """
    social = _load_social_data(ticker, as_of)

    prompt = f"""Analyse fundamental and smart money signals for {ticker} as of {as_of}.

Insider signal: {json.dumps(insider_sig, default=str)}
Institutional (13F) signal: {json.dumps(institutional_sig, default=str)}
Days to next earnings: {earnings_days if earnings_days else "unknown"}
Social activity (last 30 days): {json.dumps(social, default=str)}

Evaluate: insider buying conviction, institutional accumulation, earnings timing risk,
and retail investor interest trends.

Return JSON only:
{{
  "fundamental_score": <integer 0-10>,
  "earnings_risk": "<high|medium|low>",
  "smart_money_alignment": "<strong|moderate|weak|negative>",
  "insider_conviction": "<high|medium|low|none>",
  "avoid_earnings": <true/false — true if earnings within 7 days>,
  "retail_interest": "<high|normal|low>",
  "summary": "<one sentence>"
}}"""

    resp = _call_claude(prompt, model, SYSTEM_ANALYST)
    time.sleep(_API_DELAY_SEC)
    result = _parse_json_response(resp)
    return result if result else {
        "fundamental_score": 5, "earnings_risk": "unknown",
        "smart_money_alignment": "weak", "avoid_earnings": False,
        "summary": "Fundamental Agent unavailable",
    }


# ---------------------------------------------------------------------------
# AGENT 3: SENTIMENT AGENT
# ---------------------------------------------------------------------------

def _load_news_sentiment(ticker: str, as_of: date, lookback_days: int = 30) -> dict:
    """Load pre-fetched Finnhub news sentiment for ticker around as_of date."""
    cache_dir = Path(__file__).parent.parent / "data" / "cache" / "finnhub_news"
    path = cache_dir / f"{ticker.replace('-','_')}.parquet"
    if not path.exists():
        return {"available": False, "avg_sentiment": 0, "article_count": 0}
    try:
        df = pd.read_parquet(path)
        if df.empty:
            return {"available": False, "avg_sentiment": 0, "article_count": 0}
        df["date"] = pd.to_datetime(df["date"])
        start = pd.Timestamp(as_of) - pd.Timedelta(days=lookback_days)
        window = df[(df["date"] >= start) & (df["date"] <= pd.Timestamp(as_of))]
        if window.empty:
            return {"available": True, "avg_sentiment": 0, "article_count": 0}
        return {
            "available": True,
            "avg_sentiment": round(float(window["sentiment_mean"].mean()), 3),
            "article_count": int(window["article_count"].sum()),
            "lookback_days": lookback_days,
        }
    except Exception:
        return {"available": False, "avg_sentiment": 0, "article_count": 0}


def run_sentiment_agent(
    ticker: str,
    as_of: date,
    congressional_sig: dict,
    sentiment_snap: dict,
    model: str,
) -> dict:
    """
    Sentiment Agent: congressional trades, AAII, Fear/Greed, news sentiment.
    Returns: sentiment_score (0-10), contrarian_signal, congressional_strength, summary
    """
    news = _load_news_sentiment(ticker, as_of)

    prompt = f"""Analyse sentiment signals for {ticker} as of {as_of}.

Congressional trading signal: {json.dumps(congressional_sig, default=str)}
Market sentiment snapshot: {json.dumps(sentiment_snap, default=str)}
News sentiment (last 30 days): {json.dumps(news, default=str)}

Evaluate: Is broad market sentiment a tailwind or headwind? Are congressional signals
confirming or contradicting technical setup? Does recent news sentiment support the trade?

Return JSON only:
{{
  "sentiment_score": <integer 0-10>,
  "contrarian_signal": "<extreme_buy|buy|neutral|sell|extreme_sell>",
  "congressional_strength": "<strong_buy|buy|neutral|sell|none>",
  "fear_greed_context": "<fear_zone_opportunity|neutral|greed_zone_caution>",
  "news_sentiment": "<positive|neutral|negative|not_available>",
  "summary": "<one sentence>"
}}"""

    resp = _call_claude(prompt, model, SYSTEM_ANALYST)
    time.sleep(_API_DELAY_SEC)
    result = _parse_json_response(resp)
    return result if result else {
        "sentiment_score": 5, "contrarian_signal": "neutral",
        "congressional_strength": "none",
        "summary": "Sentiment Agent unavailable",
    }


# ---------------------------------------------------------------------------
# AGENT 4: RISK AGENT
# ---------------------------------------------------------------------------

def run_risk_agent(
    ticker: str,
    as_of: date,
    macro_snap: dict,
    sector: str,
    model: str,
) -> dict:
    """
    Risk Agent: yield curve, VIX, DXY, economic calendar, sector risk.
    Returns: risk_score (0-10, 10=lowest risk), macro_environment, trade_blocked, summary
    """
    prompt = f"""Assess macro and risk environment for {ticker} (sector: {sector}) as of {as_of}.

Macro snapshot: {json.dumps(macro_snap, default=str)}

Evaluate: Is the macro environment favourable for a new swing trade entry?
Consider: yield curve regime, VIX level, DXY trend, proximity to major events.

Return JSON only:
{{
  "risk_score": <integer 0-10, where 10 = best/safest macro environment>,
  "macro_environment": "<favourable|neutral|unfavourable>",
  "trade_blocked": <true/false — true if near major event OR VIX crisis>,
  "vix_concern": "<none|moderate|high>",
  "yield_curve_concern": "<none|moderate|high>",
  "summary": "<one sentence>"
}}"""

    resp = _call_claude(prompt, model, SYSTEM_ANALYST)
    time.sleep(_API_DELAY_SEC)
    result = _parse_json_response(resp)
    return result if result else {
        "risk_score": 5, "macro_environment": "neutral",
        "trade_blocked": macro_snap.get("near_high_impact_event", False),
        "summary": "Risk Agent unavailable",
    }


# ---------------------------------------------------------------------------
# AGENTS 5a/5b: BULL/BEAR DEBATE
# ---------------------------------------------------------------------------

def run_bull_bear_debate(
    ticker: str,
    as_of: date,
    tech_result: dict,
    fundamental_result: dict,
    sentiment_result: dict,
    risk_result: dict,
    model: str,
) -> dict:
    """
    Bull and Bear agents debate the full signal set.
    Returns: bull_score, bear_score, debate_winner, key_bull_argument, key_bear_argument
    """
    combined_context = {
        "technical":    tech_result,
        "fundamental":  fundamental_result,
        "sentiment":    sentiment_result,
        "risk":         risk_result,
    }

    prompt = f"""You are running a bull/bear debate for {ticker} swing trade entry as of {as_of}.

Full signal context:
{json.dumps(combined_context, indent=2, default=str)}

Argue BOTH sides objectively. Bull case: why this trade should be taken.
Bear case: why it should be avoided. Then decide which is stronger.

Return JSON only:
{{
  "bull_score": <integer 0-10>,
  "bear_score": <integer 0-10>,
  "debate_winner": "<bull|bear|neutral>",
  "key_bull_argument": "<one sentence>",
  "key_bear_argument": "<one sentence>",
  "confidence_in_winner": "<high|medium|low>"
}}"""

    resp = _call_claude(prompt, model, SYSTEM_ANALYST, max_tokens=600)
    time.sleep(_API_DELAY_SEC)
    result = _parse_json_response(resp)
    return result if result else {
        "bull_score": 5, "bear_score": 5, "debate_winner": "neutral",
        "confidence_in_winner": "low",
    }


# ---------------------------------------------------------------------------
# AGENT 6: DECISION AGENT
# ---------------------------------------------------------------------------

def run_decision_agent(
    ticker: str,
    as_of: date,
    all_agent_results: dict,
    smart_money_score: dict,
    model: str,
) -> dict:
    """
    Decision Agent: synthesises all agent outputs into final trade recommendation.
    Returns: final_score (0-100), confidence_tier, action, stop_loss_atr, take_profit_atr
    """
    prompt = f"""Make final trade decision for {ticker} swing trade as of {as_of}.

All agent outputs:
{json.dumps(all_agent_results, indent=2, default=str)}

Smart money composite: {json.dumps(smart_money_score, default=str)}

Synthesise all signals. Apply the confidence matrix:
- EXCEPTIONAL (score 85+): 3+ tech strategies + congressional + insider cluster buy
- VERY HIGH (70-84): 2+ tech strategies + congressional OR insider buy
- HIGH (60-69): 3+ strategies, no smart money
- MEDIUM-HIGH (50-59): 2 strategies, no smart money
- MEDIUM (40-49): 1 strategy + any smart money buy
- LOW (<40): 1 strategy only
- AVOID: any STRONG_NEGATIVE smart money signal

Return JSON only:
{{
  "final_score": <integer 0-100>,
  "confidence_tier": "<EXCEPTIONAL|VERY_HIGH|HIGH|MEDIUM_HIGH|MEDIUM|LOW|AVOID>",
  "action": "<TAKE_TRADE|WATCHLIST|SKIP|AVOID>",
  "entry_rationale": "<one sentence>",
  "primary_risk": "<one sentence>",
  "stop_loss_atr_multiple": 2.0,
  "take_profit_atr_multiple": 3.0
}}"""

    resp = _call_claude(prompt, model, SYSTEM_ANALYST, max_tokens=500)
    time.sleep(_API_DELAY_SEC)
    result = _parse_json_response(resp)
    return result if result else {
        "final_score": 40, "confidence_tier": "MEDIUM",
        "action": "WATCHLIST", "stop_loss_atr_multiple": 2.0,
        "take_profit_atr_multiple": 3.0,
    }


import hashlib
from pathlib import Path

AGENT_CACHE_DIR = Path(__file__).parent / "cache"


def _agent_cache_key(ticker: str, as_of: date, strategies: list, phase: str) -> str:
    """Generate a unique cache key for this agent run."""
    strat_str = "_".join(sorted(strategies)) if strategies else "none"
    raw = f"{ticker}_{as_of}_{strat_str}_{phase}"
    return hashlib.md5(raw.encode()).hexdigest()


def _load_agent_cache(cache_key: str) -> Optional[dict]:
    """Load cached agent result if it exists."""
    AGENT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = AGENT_CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except Exception:
            return None
    return None


def _save_agent_cache(cache_key: str, result: dict):
    """Save agent result to cache."""
    try:
        AGENT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = AGENT_CACHE_DIR / f"{cache_key}.json"
        cache_file.write_text(json.dumps(result, default=str))
    except Exception as exc:
        logger.warning("Agent cache write failed: %s", exc)


# ---------------------------------------------------------------------------
# FULL PIPELINE ORCHESTRATOR
# ---------------------------------------------------------------------------

def run_full_agent_pipeline(
    ticker: str,
    as_of: date,
    candidate: dict,
    smart_money_data: dict,
    macro_snap: dict,
    sentiment_snap: dict,
    sector: str,
    earnings_days: Optional[int],
    phase: str = "phase_1a",
) -> dict:
    """
    Run all six agents for a single candidate instrument.

    Results are cached to backtest/agents/cache/ — if a run crashes and restarts,
    already-computed agent analyses are loaded from cache instead of re-calling the API.
    This prevents losing API spend on partial runs.

    Parameters:
      candidate:        output of screener.screen_instrument (contains signals)
      smart_money_data: dict with keys congressional_sig, insider_sig, institutional_sig,
                        smart_money_composite
      macro_snap:       output of macro.macro_snapshot
      sentiment_snap:   output of sentiment.sentiment_snapshot
      sector:           company sector string
      earnings_days:    days to next earnings (None if unknown)
      phase:            which phase (determines model)

    Returns: full dict of all agent outputs + final decision
    """
    model = AI_MODELS.get(phase, AI_MODELS["phase_1a"])
    signals = candidate.get("signals", {})
    strategies = candidate.get("strategies_triggered", [])

    # Check cache first — avoid re-calling API on rerun
    cache_key = _agent_cache_key(ticker, as_of, strategies, phase)
    cached = _load_agent_cache(cache_key)
    if cached:
        logger.debug("Agent cache hit: %s [%s]", ticker, as_of)
        return cached

    logger.info("Running agent pipeline: %s [%s] model=%s", ticker, as_of, model)

    # Agent 1: Technical
    tech = run_technical_agent(ticker, as_of, signals, strategies, model)

    # Agent 2: Fundamental
    fund = run_fundamental_agent(
        ticker, as_of,
        smart_money_data.get("insider_sig", {}),
        smart_money_data.get("institutional_sig", {}),
        earnings_days,
        model,
    )

    # Agent 3: Sentiment
    sent = run_sentiment_agent(
        ticker, as_of,
        smart_money_data.get("congressional_sig", {}),
        sentiment_snap,
        model,
    )

    # Agent 4: Risk
    risk = run_risk_agent(ticker, as_of, macro_snap, sector, model)

    # Agents 5: Bull/Bear debate
    debate = run_bull_bear_debate(ticker, as_of, tech, fund, sent, risk, model)

    # Agent 6: Decision
    all_results = {
        "technical":   tech,
        "fundamental": fund,
        "sentiment":   sent,
        "risk":        risk,
        "debate":      debate,
    }
    decision = run_decision_agent(
        ticker, as_of, all_results,
        smart_money_data.get("smart_money_composite", {}),
        model,
    )

    result = {
        "ticker":      ticker,
        "as_of":       str(as_of),
        "phase":       phase,
        "model":       model,
        "strategies_triggered": strategies,
        "strategy_count": candidate.get("strategy_count", 0),
        "tech_signal_count": candidate.get("tech_signal_count", 0),
        "agents": {
            "technical":   tech,
            "fundamental": fund,
            "sentiment":   sent,
            "risk":        risk,
            "debate":      debate,
            "decision":    decision,
        },
        "final_score":      decision.get("final_score", 0),
        "confidence_tier":  decision.get("confidence_tier", "LOW"),
        "action":           decision.get("action", "SKIP"),
        "entry_rationale":  decision.get("entry_rationale", ""),
        "primary_risk":     decision.get("primary_risk", ""),
    }

    # Save to cache — protects against losing API spend if run crashes
    _save_agent_cache(cache_key, result)
    return result
