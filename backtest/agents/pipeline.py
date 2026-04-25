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


PROMPT_VERSION = "v2.0"  # Increment when agent prompts change materially

def _call_claude(
    prompt: str,
    model: str,
    system: str = "",
    max_tokens: int = 800,
    temperature: float = 0.0,  # 0 = deterministic for backtest reproducibility
) -> Optional[str]:
    """
    Call Anthropic API and return the text response.
    Returns None on failure.
    temperature=0.0 for backtest (reproducible), 0.3 for live trading (some variation).
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
        "model":       model,
        "max_tokens":  max_tokens,
        "temperature": temperature,
        "messages":    [{"role": "user", "content": prompt}],
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
    gov_contracts: dict,
    lobbying: dict,
    model: str,
) -> dict:
    """
    Fundamental Agent: earnings risk, insider/13F, gov contracts, lobbying, social.
    """
    social = _load_social_data(ticker, as_of)

    earnings_context = (
        f"{earnings_days} days away — heightened volatility risk"
        if earnings_days and earnings_days < 14
        else f"{earnings_days} days away" if earnings_days
        else "unknown"
    )

    prompt = f"""Analyse fundamental and smart money signals for {ticker} as of {as_of}.

Insider signal: {json.dumps(insider_sig, default=str)}
Institutional (13F) signal: {json.dumps(institutional_sig, default=str)}
Next earnings: {earnings_context}
Government contracts (last 12 months): {json.dumps(gov_contracts, default=str)}
Lobbying activity (last 12 months): {json.dumps(lobbying, default=str)}
Social activity (last 30 days): {json.dumps(social, default=str)}

Evaluate: insider buying conviction, institutional accumulation, government contract momentum
(a company winning large contracts signals revenue visibility), lobbying spend direction
(rising spend may indicate regulatory risk or opportunity), and retail interest trends.
Note: earnings proximity increases risk but does NOT block the trade — agents assess accordingly.

Return JSON only:
{{
  "fundamental_score": <integer 0-10>,
  "earnings_risk": "<high|medium|low>",
  "smart_money_alignment": "<strong|moderate|weak|negative>",
  "insider_conviction": "<high|medium|low|none>",
  "gov_contract_signal": "<bullish|neutral|no_data>",
  "lobbying_signal": "<high_activity|moderate|low|no_data>",
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
    """
    Load pre-fetched Alpha Vantage News & Sentiment for ticker around as_of date.
    Falls back to Finnhub cache if AV cache not present.
    AV provides AI-powered sentiment scores — superior to keyword-based scoring.
    """
    # Try Alpha Vantage cache first
    av_dir = Path(__file__).parent.parent / "data" / "cache" / "av_news"
    fh_dir = Path(__file__).parent.parent / "data" / "cache" / "finnhub_news"

    for cache_dir, source in [(av_dir, "alphavantage"), (fh_dir, "finnhub")]:
        path = cache_dir / f"{ticker.replace('-','_').replace('.','_')}.parquet"
        if not path.exists():
            continue
        try:
            df = pd.read_parquet(path)
            if df.empty:
                continue
            df["date"] = pd.to_datetime(df["date"])
            start  = pd.Timestamp(as_of) - pd.Timedelta(days=lookback_days)
            window = df[(df["date"] >= start) & (df["date"] <= pd.Timestamp(as_of))]
            if window.empty:
                return {"available": True, "source": source,
                        "avg_sentiment": 0, "article_count": 0}

            # Use weighted sentiment if available (AV), else mean
            score_col = "sentiment_weighted" if "sentiment_weighted" in window.columns \
                        else "sentiment_mean"
            avg = float(window[score_col].mean()) if score_col in window.columns \
                  else float(window["sentiment_mean"].mean())

            result = {
                "available":      True,
                "source":         source,
                "avg_sentiment":  round(avg, 3),
                "article_count":  int(window["article_count"].sum()),
                "lookback_days":  lookback_days,
            }
            if "sentiment_direction" in window.columns:
                result["direction"] = window["sentiment_direction"].mode().iloc[0] \
                                      if not window.empty else "neutral"
            return result
        except Exception:
            continue

    return {"available": False, "avg_sentiment": 0, "article_count": 0}


def run_sentiment_agent(
    ticker: str,
    as_of: date,
    congressional_sig: dict,
    congressional_detail: list,
    sentiment_snap: dict,
    model: str,
) -> dict:
    """Sentiment Agent: congressional trades with detail, AAII, Fear/Greed, news."""
    news = _load_news_sentiment(ticker, as_of)

    prompt = f"""Analyse sentiment signals for {ticker} as of {as_of}.

Congressional trading signal (composite): {json.dumps(congressional_sig, default=str)}
Recent congressional trades (most recent 3):
{json.dumps(congressional_detail, indent=2, default=str)}

Market sentiment: {json.dumps(sentiment_snap, default=str)}
News sentiment (last 30 days): {json.dumps(news, default=str)}

Evaluate: Are influential politicians (large amounts, senior members) buying or selling?
Is broad market fear/greed context a contrarian opportunity or a warning?
Does recent news sentiment confirm or contradict the technical setup?

Return JSON only:
{{
  "sentiment_score": <integer 0-10>,
  "contrarian_signal": "<extreme_buy|buy|neutral|sell|extreme_sell>",
  "congressional_strength": "<strong_buy|buy|neutral|sell|none>",
  "congressional_conviction": "<high — large amount senior member|medium|low — small amount junior member|none>",
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
    earnings_days: Optional[int],
    model: str,
) -> dict:
    """Risk Agent: yield curve, VIX, DXY, earnings proximity, sector risk."""
    earnings_context = (
        f"CRITICAL: earnings in {earnings_days} days — binary event risk is high"
        if earnings_days and earnings_days <= 7
        else f"earnings in {earnings_days} days — moderate event risk"
        if earnings_days and earnings_days <= 14
        else f"earnings in {earnings_days} days" if earnings_days
        else "earnings date unknown"
    )

    prompt = f"""Assess macro and risk environment for {ticker} (sector: {sector}) as of {as_of}.

Macro snapshot: {json.dumps(macro_snap, default=str)}
Earnings proximity: {earnings_context}

Evaluate: Is the macro environment favourable? Consider yield curve regime (inversion = recession risk),
VIX level (>30 = high fear, >40 = crisis), DXY trend (strong dollar = headwind for multinationals),
corporate spread (BAA10Y — rising = credit stress), and earnings binary event risk.
Note: earnings proximity increases risk but does NOT block the trade.

Return JSON only:
{{
  "risk_score": <integer 0-10, where 10 = best/safest>,
  "macro_environment": "<favourable|neutral|unfavourable>",
  "earnings_risk": "<critical — within 7 days|high — within 14|moderate|low>",
  "vix_concern": "<none|moderate|high|crisis>",
  "yield_curve_concern": "<none|moderate|high — inverted>",
  "credit_spread_concern": "<none|moderate|high>",
  "dxy_impact": "<headwind|neutral|tailwind>",
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
    price_context: dict,
    strategies_triggered: list,
    model: str,
) -> dict:
    """Bull and Bear agents debate the full signal set with price context."""
    combined_context = {
        "technical":    tech_result,
        "fundamental":  fundamental_result,
        "sentiment":    sentiment_result,
        "risk":         risk_result,
        "price_context": price_context,
        "strategies_triggered": strategies_triggered,
    }

    prompt = f"""You are running a bull/bear debate for {ticker} swing trade entry as of {as_of}.

Full signal context:
{json.dumps(combined_context, indent=2, default=str)}

Price context: stock is {price_context.get('pct_from_52w_high', 0):+.1f}% from 52-week high,
{price_context.get('pct_from_52w_low', 0):+.1f}% from 52-week low.
Nearest support: {price_context.get('nearest_support', 'unknown')},
nearest resistance: {price_context.get('nearest_resistance', 'unknown')}.

Argue BOTH sides objectively. Consider price positioning relative to support/resistance.
Bull case: why this trade should be taken now.
Bear case: why it should be avoided or waited on. Then decide which is stronger.

Return JSON only:
{{
  "bull_score": <integer 0-10>,
  "bear_score": <integer 0-10>,
  "debate_winner": "<bull|bear|neutral>",
  "key_bull_argument": "<one sentence>",
  "key_bear_argument": "<one sentence>",
  "confidence_in_winner": "<high|medium|low>",
  "price_positioning": "<at_support — strong entry|middle_of_range|near_resistance — weak entry>"
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
    earnings_days: Optional[int],
    sector: str,
    model: str,
) -> dict:
    """Decision Agent: synthesises all agent outputs into final recommendation."""
    sector_volatility = {
        "Energy": "high", "Information Technology": "high",
        "Health Care": "high", "Communication Services": "medium",
        "Financials": "medium", "Industrials": "medium",
        "Consumer Discretionary": "medium", "Materials": "medium",
        "Consumer Staples": "low", "Utilities": "low", "Real Estate": "low",
    }.get(sector, "medium")

    prompt = f"""Make final trade decision for {ticker} swing trade as of {as_of}.

Sector: {sector} (volatility: {sector_volatility})
Earnings proximity: {f'{earnings_days} days' if earnings_days else 'unknown'} — factor into sizing, NOT go/no-go.
Smart money composite: {json.dumps(smart_money_score, default=str)}

All agent outputs:
{json.dumps(all_agent_results, indent=2, default=str)}

Synthesise all agent scores and reasoning. Assess:
1. Technical quality — how strong and confluent are the signals?
2. Fundamental alignment — do smart money signals confirm the technical setup?
3. Sentiment context — is the market environment supportive?
4. Risk profile — what is the macro and event risk?
5. Bull vs bear balance — which case is stronger?

Produce an independent conviction score 0-100 based purely on signal quality.
High volatility sectors warrant wider stops and potentially smaller position size.
Earnings proximity reduces recommended size but does not block the trade.

Return JSON only:
{{
  "final_score": <integer 0-100 — your independent conviction score>,
  "action": "<ENTER|WATCH|SKIP|AVOID>",
  "position_size_modifier": "<full|reduced_earnings|reduced_volatility|minimal>",
  "entry_rationale": "<two sentences — why enter now>",
  "primary_risk": "<one sentence — biggest risk to this trade>",
  "recommended_exit": "<atr_trail_1x|trailing_15pct|hybrid_50pct_target|next_pivot_target>",
  "agent_agreement": "<strong — all agents aligned|moderate — mostly aligned|weak — agents disagree>"
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
    """Generate a unique cache key for this agent run.
    Includes PROMPT_VERSION — changing version automatically invalidates old cache.
    """
    strat_str = "_".join(sorted(strategies)) if strategies else "none"
    raw = f"{ticker}_{as_of}_{strat_str}_{phase}_{PROMPT_VERSION}"
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
    """Run all six agents for a single candidate instrument."""
    model = AI_MODELS.get(phase, AI_MODELS["phase_1a"])
    signals = candidate.get("signals", {})
    strategies = candidate.get("strategies_triggered", [])

    # Check cache first
    cache_key = _agent_cache_key(ticker, as_of, strategies, phase)
    cached = _load_agent_cache(cache_key)
    if cached:
        logger.debug("Agent cache hit: %s [%s]", ticker, as_of)
        return cached

    logger.info("Running agent pipeline: %s [%s] model=%s", ticker, as_of, model)

    # Load additional Quiver data not in smart_money_data
    from backtest.data.smart_money import (
        get_gov_contracts, get_lobbying, get_congressional_detail
    )
    gov_contracts  = get_gov_contracts(ticker, as_of)
    lobbying       = get_lobbying(ticker, as_of)
    cong_detail    = get_congressional_detail(ticker, as_of, top_n=3)

    # Price context for agents
    price = signals.get("close", 0)
    high_52w = signals.get("high_52w", price)
    low_52w  = signals.get("low_52w", price)
    pct_from_52w_high = round((price / high_52w - 1) * 100, 1) if high_52w else 0
    pct_from_52w_low  = round((price / low_52w - 1) * 100, 1) if low_52w else 0
    nearest_support = signals.get("s1", signals.get("cam_s3", 0))
    nearest_resist  = signals.get("r1", signals.get("cam_r3", 0))
    price_context = {
        "price": price,
        "pct_from_52w_high": pct_from_52w_high,
        "pct_from_52w_low": pct_from_52w_low,
        "nearest_support": nearest_support,
        "nearest_resistance": nearest_resist,
        "above_200ema": signals.get("above_200ema", False),
        "above_50sma": signals.get("above_50sma", False),
    }

    # Agent 1: Technical
    tech = run_technical_agent(ticker, as_of, signals, strategies, model)

    # Agent 2: Fundamental — now includes gov_contracts + lobbying
    fund = run_fundamental_agent(
        ticker, as_of,
        smart_money_data.get("insider_sig", {}),
        smart_money_data.get("institutional_sig", {}),
        earnings_days,
        gov_contracts,
        lobbying,
        model,
    )

    # Agent 3: Sentiment — now includes congressional detail
    sent = run_sentiment_agent(
        ticker, as_of,
        smart_money_data.get("congressional_sig", {}),
        cong_detail,
        sentiment_snap,
        model,
    )

    # Agent 4: Risk — now includes earnings_days + DXY
    risk = run_risk_agent(
        ticker, as_of, macro_snap, sector, earnings_days, model
    )

    # Agents 5: Bull/Bear debate — now includes price context
    debate = run_bull_bear_debate(
        ticker, as_of, tech, fund, sent, risk,
        price_context, strategies, model
    )

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
        earnings_days, sector, model
    )

    # Map final_score to tier in code — agent no longer returns tier directly
    final_score = int(decision.get("final_score", 0) or 0)
    if final_score >= 85:   tier_from_score = "EXCEPTIONAL"
    elif final_score >= 70: tier_from_score = "VERY_HIGH"
    elif final_score >= 60: tier_from_score = "HIGH"
    elif final_score >= 50: tier_from_score = "MEDIUM_HIGH"
    elif final_score >= 40: tier_from_score = "MEDIUM"
    elif final_score >= 20: tier_from_score = "LOW"
    else:                   tier_from_score = "AVOID"

    result = {
        "ticker":      ticker,
        "as_of":       str(as_of),
        "phase":       phase,
        "model":       model,
        "strategies_triggered": strategies,
        "strategy_count": candidate.get("strategy_count", 0),
        "agents": {
            "technical":   tech,
            "fundamental": fund,
            "sentiment":   sent,
            "risk":        risk,
            "debate":      debate,
            "decision":    decision,
        },
        "final_score":      final_score,
        "tier_from_score":  tier_from_score,
        "action":           decision.get("action", "SKIP"),
        "entry_rationale":  decision.get("entry_rationale", ""),
        "primary_risk":     decision.get("primary_risk", ""),
        "agent_agreement":  decision.get("agent_agreement", "unknown"),
        # Context paragraph built from decision output — stored on trade
        "context_paragraph": (
            f"{decision.get('entry_rationale', '')} "
            f"Risk: {decision.get('primary_risk', '')} "
            f"Agent agreement: {decision.get('agent_agreement', 'unknown')}"
        ).strip(),
    }

    # Save to cache — protects against losing API spend if run crashes
    _save_agent_cache(cache_key, result)
    return result
