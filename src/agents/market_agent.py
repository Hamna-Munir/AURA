# src/agents/market_agent.py
from src.agents.llm import ask_json
from src.alpaca.market_data import compute_indicators
from src.utils.logger import get_logger

log = get_logger("agents.market")

SYSTEM_PROMPT = """You are the Market Agent in an autonomous trading system.
You analyze technical indicators and output a structured judgment.
You are NOT allowed to give investment advice or prose.
You ONLY return a JSON object with this exact schema:
{
  "symbol": string,
  "trend": "bullish" | "bearish" | "neutral",
  "momentum": "strong" | "weak" | "neutral",
  "volatility": "high" | "medium" | "low",
  "confidence": number between 0 and 1,
  "evidence": array of 2-4 short strings citing the specific indicators
}
Base your judgment ONLY on the numbers provided. Be objective and concise."""


def build_user_prompt(ind: dict) -> str:
    return f"""Analyze this technical snapshot and return your JSON judgment.

Symbol: {ind['symbol']}
Price: {ind['price']}
SMA20: {ind['sma20']}
SMA50: {ind['sma50']}
RSI(14): {ind['rsi']}
MACD: {ind['macd']}
MACD signal: {ind['macd_signal']}
ATR(14): {ind['atr']}
Volume: {ind['volume']}

Guidance:
- Price above both SMAs = uptrend; below both = downtrend; mixed = neutral.
- RSI > 70 overbought, < 30 oversold.
- MACD above its signal = positive momentum.
- Higher ATR relative to price = higher volatility."""


def analyze(symbol: str) -> dict:
    """Indicators laao -> Market Agent se structured judgment lo."""
    indicators = compute_indicators(symbol)
    result = ask_json(SYSTEM_PROMPT, build_user_prompt(indicators))
    log.info("Market Agent verdict for %s: %s (%.0f%%)",
             symbol, result.get("trend"), float(result.get("confidence", 0)) * 100)
    # indicators bhi saath return karte hain taake aage kaam aayein
    return {"indicators": indicators, "market_view": result}