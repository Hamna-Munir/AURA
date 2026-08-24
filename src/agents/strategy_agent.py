# src/agents/strategy_agent.py
from src.agents.llm import ask_json
from src.utils.logger import get_logger

log = get_logger("agents.strategy")

SYSTEM_PROMPT = """You are the Strategy Agent in an autonomous trading system.
You receive a technical snapshot and the Market Agent's judgment, and you
produce a concrete trade thesis. You do NOT give investment advice or prose.
You ONLY return a JSON object with this exact schema:
{
  "symbol": string,
  "action": "BUY" | "SELL" | "HOLD",
  "confidence": number between 0 and 1,
  "entry_reason": string (one sentence, cite the evidence),
  "stop_loss_distance": number (suggested stop distance in dollars, use ATR as a guide),
  "expected_risk_reward": number (e.g. 2.0 means reward is 2x the risk),
  "invalidating_conditions": array of 2-3 short strings describing what would make this trade wrong
}
Rules:
- Only propose BUY or SELL when the evidence is reasonably aligned; otherwise HOLD.
- stop_loss_distance should be roughly 1x to 2x the ATR.
- Be disciplined: a weak or mixed setup should be HOLD, not a forced trade."""


def build_user_prompt(indicators: dict, market_view: dict) -> str:
    return f"""Technical snapshot:
Symbol: {indicators['symbol']}
Price: {indicators['price']}
SMA20: {indicators['sma20']}
SMA50: {indicators['sma50']}
RSI(14): {indicators['rsi']}
MACD: {indicators['macd']}
MACD signal: {indicators['macd_signal']}
ATR(14): {indicators['atr']}

Market Agent judgment:
Trend: {market_view.get('trend')}
Momentum: {market_view.get('momentum')}
Volatility: {market_view.get('volatility')}
Confidence: {market_view.get('confidence')}
Evidence: {market_view.get('evidence')}

Produce your trade thesis as JSON."""


def decide(indicators: dict, market_view: dict) -> dict:
    """Market view -> concrete trade thesis (BUY/SELL/HOLD)."""
    thesis = ask_json(SYSTEM_PROMPT, build_user_prompt(indicators, market_view))
    log.info("Strategy Agent thesis for %s: %s (%.0f%%)",
             thesis.get("symbol"), thesis.get("action"),
             float(thesis.get("confidence", 0)) * 100)
    return thesis