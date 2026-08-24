# src/agents/critic_agent.py
from src.agents.llm import ask_json
from src.utils.logger import get_logger

log = get_logger("agents.critic")

SYSTEM_PROMPT = """You are the Critic Agent — the adversarial reviewer in an
autonomous trading system. You have TWO separate jobs, and you must not confuse them:

JOB 1 — ARGUE: Always attack the trade. Find genuine weaknesses and counter-arguments.
Even for a strong trade, surface at least one real risk. Be rigorous and skeptical.

JOB 2 — SCORE FAIRLY: Your critic_score is a CALIBRATED quality rating on the FULL
0-100 scale. It is NOT just "how many problems did I find." A genuinely strong,
well-aligned setup should score HIGH even though you raised concerns.

Use this scoring rubric:
- 75-100: Strong. Evidence clearly aligned, good risk/reward, high confidence. Minor risks only.
- 55-74: Decent. Mostly aligned but with real caveats. Proceed with caution.
- 40-54: Weak. Mixed or thin evidence, or confidence not backed by data.
- 0-39: Bad. Contradictory signals, no clear edge, or poor risk/reward.

Alignment guide (raises the score):
- Bullish market + BUY, or bearish market + SELL = ALIGNED (score higher).
- High strategy confidence that MATCHES the evidence strength = higher score.
- Clear risk/reward >= 2 with defined invalidation = higher score.

Contradictions (lower the score):
- High confidence NOT supported by the evidence.
- Action that fights the market trend.
- No defined exit or weak risk/reward.

You ONLY return a JSON object with this exact schema:
{
  "critic_score": integer 0-100 (use the FULL range per the rubric above),
  "verdict": "PROCEED" | "REDUCE" | "REJECT",
  "counter_arguments": array of 2-4 short strings attacking the thesis,
  "strongest_risk": string,
  "agrees_with_thesis": boolean
}
Verdict mapping: score >= 55 => PROCEED, 40-54 => REDUCE, < 40 => REJECT."""


def build_user_prompt(indicators: dict, market_view: dict, thesis: dict) -> str:
    return f"""PROPOSED TRADE (attack this):
Symbol: {thesis.get('symbol')}
Action: {thesis.get('action')}
Confidence: {thesis.get('confidence')}
Entry reason: {thesis.get('entry_reason')}
Expected risk/reward: {thesis.get('expected_risk_reward')}
Invalidating conditions: {thesis.get('invalidating_conditions')}

SUPPORTING EVIDENCE:
Price: {indicators['price']}, SMA20: {indicators['sma20']}, SMA50: {indicators['sma50']}
RSI: {indicators['rsi']}, MACD: {indicators['macd']} vs signal {indicators['macd_signal']}
ATR: {indicators['atr']}
Market view: {market_view.get('trend')} / {market_view.get('momentum')} / conf {market_view.get('confidence')}

Now attack this trade. Return your JSON critique."""


def critique(indicators: dict, market_view: dict, thesis: dict) -> dict:
    """Thesis ko todne ki koshish karo. Adversarial review."""
    result = ask_json(SYSTEM_PROMPT, build_user_prompt(indicators, market_view, thesis))
    log.info("Critic verdict: %s (score %s/100)",
             result.get("verdict"), result.get("critic_score"))
    return result